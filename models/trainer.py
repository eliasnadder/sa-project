import os
import random
import json
import numpy as np
import matplotlib.pyplot as plt
import glob
from concurrent.futures import ProcessPoolExecutor, as_completed

# بدون تقليم
# from players.ai import AI
# مع تقليم
from players.ai_pruning import AI

from evaluations.evaluation_ai_phased import SENET_AI_CONFIG
from engines.game_state_pyrsistent import GameState
from engines.board import create_initial_board
from engines.rules_silent import apply_move, check_win
from engines.sticks import throw_sticks
from datetime import datetime

# إعدادات محسّنة
POP_SIZE = 15
GENS = 20
MATCHES_PER_EVAL = 10
ELITE_SIZE = 6
MUTATION_RATE = 0.3
MAX_MOVES = 200

# البنية المطلوبة تماماً لكل DNA وللملفات النهائية
DESIRED_CONFIG_KEYS = {
    'piece_off': 1200,          # نقاط الخروج
    'win_bonus': 20000,         # مكافأة الفوز
    'progress_base': 85,        # أساس التقدم
    'zone_multiplier': 1.8,     # مضاعف المنطقة
    'happiness_bonus': 150,     # مكافأة خانة السعادة
    'water_penalty': -300,      # عقوبة خانة الماء
    'special_house': 100,       # مكافأة الخانات الخاصة
    'protection': 60,           # نقاط الحماية
    'block': 80,                # نقاط التكتل
    'attack': 60,               # نقاط الهجوم
    'flexibility': 8,           # نقاط المرونة
    'isolated_penalty': 15      # عقوبة القطع المعزولة
}


class Trainer:
    def __init__(self):
        self.population = []
        self.best_ever = None
        self.best_ever_score = -float('inf')
        self.stats = {
            'best_scores': [],
            'avg_scores': [],
            'diversity': []
        }
        self.start_gen = 0

    def _get_base_dna(self):
        """إرجاع DNA أساسي بالمفاتيح والقيم الافتراضية المطلوبة بالضبط"""
        return DESIRED_CONFIG_KEYS.copy()

    def _randomize_dna(self, base_dna=None):
        """إنشاء DNA عشوائي مع تنوع أفضل"""
        if base_dna is None:
            base_dna = self._get_base_dna()

        dna = {}
        for k, v in base_dna.items():
            # تنوع أكبر في البداية
            factor = random.uniform(0.5, 1.5)
            dna[k] = v * factor
        return dna

    def _init_population(self):
        """تهيئة العشيرة بتنوع أفضل"""
        print("Initializing population...")

        base = self._get_base_dna()

        # 1/3 من العشيرة بأوزان قريبة من الأصلية
        for _ in range(POP_SIZE // 3):
            dna = base.copy()
            for k in dna:
                dna[k] *= random.uniform(0.8, 1.2)
            self.population.append(dna)

        # 1/3 بتنوع متوسط
        for _ in range(POP_SIZE // 3):
            dna = base.copy()
            for k in dna:
                dna[k] *= random.uniform(0.6, 1.4)
            self.population.append(dna)

        # 1/3 بتنوع عالي
        for _ in range(POP_SIZE - 2 * (POP_SIZE // 3)):
            self.population.append(self._randomize_dna())

    def evaluate_dna(self, dna, dna_id):
        """تقييم DNA واحد بعدة مباريات"""
        wins = 0
        draws = 0

        for game_num in range(MATCHES_PER_EVAL):
            result = self.play_match(dna)
            if result == 'X':
                wins += 1
            elif result == 'DRAW':
                draws += 0.5

        # احتساب النقاط: الفوز = 3، التعادل = 1
        score = wins * 3 + draws

        return (dna_id, score, wins, dna)

    def play_match(self, dna):
        """لعب مباراة واحدة"""
        board = create_initial_board()

        # AI المدرب vs AI الأساسي
        ai_x = AI('X', depth=3, weights=dna)
        ai_o = AI('O', depth=3, weights=SENET_AI_CONFIG)

        current_player = 'X'
        move_count = 0

        # تتبع الحالات لاكتشاف التكرار
        state_history = {}

        while move_count < MAX_MOVES:
            roll = throw_sticks()

            if current_player == 'X':
                state = GameState.from_board(board, 'X')
                move = ai_x.choose_best_move(state, roll)
            else:
                state = GameState.from_board(board, 'O')
                move = ai_o.choose_best_move(state, roll)

            if move:
                board = apply_move(board, move[0], move[1])

                # فحص الفوز
                if check_win(board, current_player):
                    return current_player

                # كشف التكرار
                board_key = tuple(board)
                state_history[board_key] = state_history.get(board_key, 0) + 1
                if state_history[board_key] >= 3:
                    return 'DRAW'  # تعادل بسبب التكرار

            current_player = 'O' if current_player == 'X' else 'X'
            move_count += 1

        # تعادل بسبب انتهاء الوقت
        x_pieces = sum(1 for p in board if p == 'X')
        o_pieces = sum(1 for p in board if p == 'O')

        if x_pieces < o_pieces:
            return 'X'  # أقل قطع = أفضل
        elif o_pieces < x_pieces:
            return 'O'
        return 'DRAW'

    def _mutate(self, dna):
        """طفرة محسّنة مع تحكم أفضل"""
        new_dna = dna.copy()

        # عدد المعاملات للطفرة
        num_mutations = random.randint(1, 3)

        for _ in range(num_mutations):
            k = random.choice(list(new_dna.keys()))
            mutation_type = random.random()

            # طفرة صغيرة
            if mutation_type < 0.6:
                new_dna[k] *= random.uniform(0.85, 1.15)
            # طفرة متوسطة
            elif mutation_type < 0.9:
                new_dna[k] *= random.uniform(0.7, 1.3)
            # طفرة كبيرة (نادرة)
            else:
                new_dna[k] *= random.uniform(0.5, 1.5)

        return new_dna

    def _crossover(self, parent1, parent2):
        """تهجين محسّن"""
        child = {}

        for k in DESIRED_CONFIG_KEYS.keys():
            # أخذ من الوالد الأول
            if random.random() < 0.5:
                child[k] = parent1.get(k, DESIRED_CONFIG_KEYS[k])
            # أخذ من الوالد الثاني
            else:
                child[k] = parent2.get(k, DESIRED_CONFIG_KEYS[k])

            # إضافة ضجيج صغير
            if random.random() < 0.1:
                child[k] *= random.uniform(0.95, 1.05)

        return child

    def _calculate_diversity(self):
        """حساب تنوع العشيرة"""
        if len(self.population) < 2:
            return 0

        diversities = []
        for i in range(len(self.population)):
            for j in range(i + 1, len(self.population)):
                diff = sum(abs(self.population[i].get(k, 0) - self.population[j].get(k, 0))
                           for k in DESIRED_CONFIG_KEYS.keys())
                diversities.append(diff)

        return np.mean(diversities) if diversities else 0

    def load_checkpoint(self, filepath):
        """تحميل حالة التدريب السابقة"""
        print(f"📂 Loading checkpoint from: {filepath}")
        with open(filepath, 'r') as f:
            data = json.load(f)

        # فرض المفاتيح المطلوبة مع إضافة المفقودة بالافتراضي
        fixed_best = self._get_base_dna()
        fixed_best.update(data.get('best_weights', {}))
        self.best_ever = fixed_best
        self.best_ever_score = data.get('best_score', -float('inf'))
        self.stats = data.get(
            'stats', {'best_scores': [], 'avg_scores': [], 'diversity': []})

        # استرجاع العشيرة (مهم جداً للاستمرار)
        if 'population' in data:
            self.population = []
            for old_dna in data['population']:
                fixed_dna = self._get_base_dna()
                fixed_dna.update(old_dna)
                self.population.append(fixed_dna)
        else:
            print(
                "⚠️ Warning: No population in checkpoint. Generating new from best weights.")
            self.population = [self.best_ever.copy() for _ in range(POP_SIZE)]

        self.start_gen = data.get('generation', 0)

        print(f"✅ Resumed from Generation {self.start_gen}")
        print(f"   Best Score so far: {self.best_ever_score}")

    def run(self, resume_file=None):
        """تشغيل التدريب المحسّن"""
        print("=" * 60)
        print("Starting Improved Evolutionary Training")
        print(f"Population: {POP_SIZE}, Generations: {GENS}")
        print(f"Matches per eval: {MATCHES_PER_EVAL}")
        print("=" * 60)

        # منطق الاستئناف
        if resume_file:
            self.load_checkpoint(resume_file)
        elif not self.population:
            self._init_population()

        for gen in range(self.start_gen, GENS):
            print(f"\n{'='*60}")
            print(f"Generation {gen + 1}/{GENS}")
            print(f"{'='*60}")

            # تقييم كل العشيرة
            results = []
            with ProcessPoolExecutor() as executor:
                futures = [executor.submit(self.evaluate_dna, dna, i)
                           for i, dna in enumerate(self.population)]
                for future in as_completed(futures):
                    results.append(future.result())
                    print(
                        f"  Evaluated {len(results)}/{len(self.population)} DNAs...", end='\r')

            # سطر جديد
            print()

            # ترتيب حسب النقاط
            results.sort(key=lambda x: x[1], reverse=True)

            # إحصائيات
            scores = [r[1] for r in results]
            best_score = scores[0]
            avg_score = np.mean(scores)
            diversity = self._calculate_diversity()

            self.stats['best_scores'].append(best_score)
            self.stats['avg_scores'].append(avg_score)
            self.stats['diversity'].append(diversity)

            # تحديث الأفضل على الإطلاق
            if best_score > self.best_ever_score:
                self.best_ever_score = best_score
                self.best_ever = results[0][3].copy()
                print(f"  🏆 NEW BEST EVER! Score: {best_score:.2f}")

            print(f"  Best score: {best_score:.2f}")
            print(f"  Avg score: {avg_score:.2f}")
            print(f"  Worst score: {scores[-1]:.2f}")
            print(f"  Diversity: {diversity:.2f}")
            print(f"  Best DNA wins: {results[0][2]}/{MATCHES_PER_EVAL}")

            # إنشاء الجيل الجديد
            new_population = []

            # 1. الاحتفاظ بالنخبة
            for _, _, _, dna in results[:ELITE_SIZE]:
                new_population.append(dna.copy())

            # 2. تهجين وطفرات
            while len(new_population) < POP_SIZE:
                # اختيار والدين من أفضل 50%
                parent1 = random.choice([r[3] for r in results[:POP_SIZE//2]])
                parent2 = random.choice([r[3] for r in results[:POP_SIZE//2]])

                # تهجين
                child = self._crossover(parent1, parent2)

                # طفرة
                if random.random() < MUTATION_RATE:
                    child = self._mutate(child)

                new_population.append(child)

            self.population = new_population

            # حفظ الأفضل كل 5 أجيال
            if (gen + 1) % 5 == 0:
                self._save_checkpoint(gen + 1)

        # حفظ النتيجة النهائية
        print("\n" + "=" * 60)
        print("Training Complete!")
        print(f"Best score achieved: {self.best_ever_score:.2f}")
        print("=" * 60)

        self._save_final_results()
        self._plot_results()

    def _save_checkpoint(self, gen):
        """حفظ نقطة تفتيش"""
        filename = f"checkpoints/checkpoint_gen_{gen}.json"
        os.makedirs("checkpoints", exist_ok=True)
        data = {
            'generation': gen,
            'best_weights': self.best_ever,
            'best_score': self.best_ever_score,
            'stats': self.stats,
            'population': self.population
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"  💾 Checkpoint saved: {filename}")

    def _save_final_results(self):
        """حفظ النتائج النهائية"""
        # حفظ الأوزان الأفضل
        with open("best_ai_weights_improved.json", "w") as f:
            json.dump(self.best_ever, f, indent=4)

        # حفظ الإحصائيات مع الأوزان النهائية للمقارنة المستقبلية
        stats_with_weights = self.stats.copy()
        stats_with_weights['final_weights'] = self.best_ever
        stats_with_weights['final_score'] = self.best_ever_score

        with open("training_stats.json", "w") as f:
            json.dump(stats_with_weights, f, indent=4)

        # حفظ نسخة احتياطية مع التاريخ
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_weights = f"backups/weights_{timestamp}.json"
        backup_stats = f"backups/stats_{timestamp}.json"

        # إنشاء مجلد backups إذا لم يكن موجوداً
        os.makedirs("backups", exist_ok=True)

        with open(backup_weights, "w") as f:
            json.dump(self.best_ever, f, indent=4)

        with open(backup_stats, "w") as f:
            json.dump(stats_with_weights, f, indent=4)

        print("\n✅ Results saved with exact desired keys:")
        print("  - best_ai_weights_improved.json")
        print("  - training_stats.json")
        print(f"  - {backup_weights}")
        print(f"  - {backup_stats}")

    def _plot_results(self):
        """رسم النتائج مع مقارنة بالتدريب السابق"""

        # محاولة تحميل النتائج السابقة
        previous_stats = self._load_previous_stats()

        # إنشاء اسم الملف مع التاريخ والوقت
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'training_progress_{timestamp}.png'

        # تحديد حجم الرسم بناءً على وجود بيانات سابقة
        if previous_stats:
            fig = plt.figure(figsize=(16, 12))
            gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        else:
            fig = plt.figure(figsize=(14, 10))
            gs = fig.add_gridspec(3, 1, hspace=0.3)

        # ========== الرسم 1: تقدم النقاط ==========
        if previous_stats:
            ax1 = fig.add_subplot(gs[0, :])
        else:
            ax1 = fig.add_subplot(gs[0, 0])

        # رسم النتائج الحالية
        generations = list(range(1, len(self.stats['best_scores']) + 1))

        ax1.plot(generations, self.stats['best_scores'],
                 label='Best Score (Current)', linewidth=2.5,
                 marker='o', markersize=4, color='#2E86AB')
        ax1.plot(generations, self.stats['avg_scores'],
                 label='Average Score (Current)', linewidth=2.5,
                 marker='s', markersize=4, color='#A23B72')

        # رسم النتائج السابقة إذا وجدت
        if previous_stats and 'best_scores' in previous_stats:
            prev_gens = list(range(1, len(previous_stats['best_scores']) + 1))
            ax1.plot(prev_gens, previous_stats['best_scores'],
                     label='Best Score (Previous)', linewidth=2,
                     linestyle='--', alpha=0.6, color='#2E86AB')
            ax1.plot(prev_gens, previous_stats['avg_scores'],
                     label='Average Score (Previous)', linewidth=2,
                     linestyle='--', alpha=0.6, color='#A23B72')

        ax1.set_xlabel('Generation', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Score', fontsize=11, fontweight='bold')
        ax1.set_title('Training Progress - Score Evolution',
                      fontsize=13, fontweight='bold', pad=15)
        ax1.legend(loc='best', fontsize=9)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_xlim(left=0)

        # إضافة خط أفقي للأفضل على الإطلاق
        ax1.axhline(y=self.best_ever_score, color='gold', linestyle=':', linewidth=2, alpha=0.7,
                    label=f'Best Ever: {self.best_ever_score:.2f}')

        # ========== الرسم 2: التنوع ==========
        if previous_stats:
            ax2 = fig.add_subplot(gs[1, 0])
        else:
            ax2 = fig.add_subplot(gs[1, 0])

        ax2.plot(generations, self.stats['diversity'],
                 label='Diversity (Current)', linewidth=2.5,
                 color='#06A77D', marker='^', markersize=4)

        if previous_stats and 'diversity' in previous_stats:
            prev_gens = list(range(1, len(previous_stats['diversity']) + 1))
            ax2.plot(prev_gens, previous_stats['diversity'],
                     label='Diversity (Previous)', linewidth=2,
                     linestyle='--', alpha=0.6, color='#06A77D')

        ax2.set_xlabel('Generation', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Diversity Score', fontsize=11, fontweight='bold')
        ax2.set_title('Population Diversity Over Time',
                      fontsize=13, fontweight='bold', pad=15)
        ax2.legend(loc='best', fontsize=9)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_xlim(left=0)

        # ========== الرسم 3: معدل التحسن ==========
        if previous_stats:
            ax3 = fig.add_subplot(gs[1, 1])
        else:
            ax3 = fig.add_subplot(gs[2, 0])

        # حساب معدل التحسن بين الأجيال
        if len(self.stats['best_scores']) > 1:
            improvements = [self.stats['best_scores'][i] - self.stats['best_scores'][i-1]
                            for i in range(1, len(self.stats['best_scores']))]
            improvement_gens = list(
                range(2, len(self.stats['best_scores']) + 1))
            colors = ['green' if imp > 0 else 'red' if imp <
                      0 else 'gray' for imp in improvements]

            ax3.bar(improvement_gens, improvements,
                    color=colors, alpha=0.7, width=0.8)
            ax3.set_xlabel('Generation', fontsize=11, fontweight='bold')
            ax3.set_ylabel('Score Improvement', fontsize=11, fontweight='bold')
            ax3.set_title('Generation-to-Generation Improvement',
                          fontsize=13, fontweight='bold', pad=15)
            ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax3.grid(True, alpha=0.3, linestyle='--', axis='y')
            ax3.set_xlim(left=1)

        # ========== الرسم 4: مقارنة الأوزان (إذا وجدت نتائج سابقة) ==========
        if previous_stats and 'final_weights' in previous_stats:
            ax4 = fig.add_subplot(gs[2, :])

            # مقارنة الأوزان النهائية
            weight_keys = list(DESIRED_CONFIG_KEYS.keys())
            x = np.arange(len(weight_keys))
            width = 0.35

            current_vals = [self.best_ever.get(k, 0) for k in weight_keys]
            previous_vals = [previous_stats['final_weights'].get(
                k, 0) for k in weight_keys]

            ax4.bar(x - width/2, previous_vals, width,
                    label='Previous Best', alpha=0.7, color='#95B8D1')
            ax4.bar(x + width/2, current_vals, width,
                    label='Current Best', alpha=0.7, color='#E09F3E')

            ax4.set_xlabel('Weight Parameters')
            ax4.set_ylabel('Weight Value')
            ax4.set_title('Final Weights Comparison: Previous vs Current')
            ax4.set_xticks(x)
            ax4.set_xticklabels(weight_keys, rotation=45, ha='right')
            ax4.legend(loc='best')
            ax4.grid(True, alpha=0.3, axis='y')
            ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

            # إضافة قيم فوق الأعمدة
            for bars in ax4.containers:
                for bar in bars:
                    height = bar.get_height()
                    # فقط للقيم الكبيرة
                    if abs(height) > 10:
                        ax4.text(bar.get_x() + bar.get_width()/2., height,
                                 f'{height:.0f}', ha='center',
                                 va='bottom' if height > 0 else 'top', fontsize=7, alpha=0.7)

        # ========== إضافة معلومات التدريب ==========
        info_text = f"""Training Configuration:
Population Size: {POP_SIZE}
Generations: {GENS}
Matches per Eval: {MATCHES_PER_EVAL}
Best Score: {self.best_ever_score:.2f}
Final Avg Score: {self.stats['avg_scores'][-1]:.2f if self.stats['avg_scores'] else 0:.2f}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""

        fig.text(0.02, 0.02, info_text, fontsize=8, family='monospace',
                 verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        # ========== حفظ الرسم ==========
        plt.suptitle('Senet AI Training Results - Genetic Algorithm Evolution',
                     fontsize=16, fontweight='bold', y=0.995)

        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"  📊 Visualization saved: {filename}")

        # حفظ نسخة أيضاً بدون تاريخ (للوصول السريع)
        latest_filename = 'training_progress_latest.png'
        plt.savefig(latest_filename, dpi=300, bbox_inches='tight')
        print(f"  📊 Latest copy saved: {latest_filename}")

        plt.show()

    def _load_previous_stats(self):
        """تحميل إحصائيات التدريب السابق"""
        try:
            with open("training_stats.json", 'r') as f:
                previous_stats = json.load(f)
            print("  📂 Loaded previous training stats for comparison")
            return previous_stats
        except FileNotFoundError:
            print("  ℹ️  No previous training stats found")
            return None


def get_latest_checkpoint():
    files = glob.glob("checkpoints/checkpoint_gen_*.json")
    if not files:
        return None

    # استخراج رقم الجيل من اسم الملف للترتيب الصحيح
    # المتوقع: checkpoint_gen_10.json
    try:
        latest_file = max(files, key=lambda f: int(
            f.split('_gen_')[1].split('.')[0]))
        return latest_file
    except:
        return max(files, key=os.path.getmtime)


if __name__ == "__main__":
    trainer = Trainer()

    # البحث عن ملفات حفظ سابقة
    latest_checkpoint = get_latest_checkpoint()

    if latest_checkpoint:
        print(
            f"\n🔔 Found existing checkpoint: {os.path.basename(latest_checkpoint)}")
        print("Options:")
        print(
            "  [r] Resume training from checkpoint (إعادة التحميل من نقطة معينة وإكمال التدريب)")
        print("  [l] Load best weights from previous file and train on it (استخدام الملف السابق كدخل للتدريب عليه)")
        print(
            "  [n] Start NEW training from scratch (التدريب من البداية دون استخدام الملف)")

        choice = input("Enter choice (r/l/n): ").strip().lower()

        if choice == 'r':
            trainer.run(latest_checkpoint)
        elif choice == 'l':
            print("Loading best weights and creating new population...")
            with open(latest_checkpoint, 'r') as f:
                data = json.load(f)
            fixed_best = trainer._get_base_dna()
            fixed_best.update(data.get('best_weights', {}))
            trainer.best_ever = fixed_best
            trainer.best_ever_score = data.get('best_score', -float('inf'))
            trainer.stats = {'best_scores': [],
                             'avg_scores': [], 'diversity': []}
            trainer.start_gen = 0
            trainer.population = []
            for _ in range(POP_SIZE):
                trainer.population.append(
                    trainer._mutate(trainer.best_ever.copy()))
            trainer.run(None)
        elif choice == 'n':
            print("⚠️ Starting fresh training...")
            trainer.run(None)
        else:
            print("Invalid choice. Starting fresh training...")
            trainer.run(None)
    else:
        print("No previous checkpoint found. Starting new training...")
        trainer.run(None)
