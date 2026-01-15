import json
import matplotlib.pyplot as plt
import numpy as np
# from ai import AI
from ai_improved import ImprovedAI as AI
from game_state_pyrsistent import GameState
from board import create_initial_board
from rules import apply_move, check_win
from sticks import throw_sticks
from evaluation_ai import SENET_AI_CONFIG


class WeightsAnalyzer:
    """أداة تحليل شاملة لأوزان الـ AI"""

    def __init__(self):
        self.baseline_weights = SENET_AI_CONFIG.copy()
        self.trained_weights = None

    def load_trained_weights(self, filename="best_ai_weights.json"):
        """تحميل الأوزان المدربة"""
        try:
            with open(filename, 'r') as f:
                self.trained_weights = json.load(f)
            print(f"✅ Loaded weights from {filename}")
            return True
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
            return False

    def compare_weights(self):
        """مقارنة الأوزان"""
        if not self.trained_weights:
            print("❌ No trained weights loaded!")
            return

        print("\n" + "="*80)
        print("WEIGHTS COMPARISON")
        print("="*80)
        print(
            f"{'Parameter':<20} {'Baseline':>12} {'Trained':>12} {'Change':>12} {'Change %':>12}")
        print("-"*80)

        for key in self.baseline_weights.keys():
            base_val = self.baseline_weights[key]
            trained_val = self.trained_weights.get(key, base_val)
            change = trained_val - base_val
            change_pct = (change / base_val * 100) if base_val != 0 else 0

            # علامة تحذير للتغييرات الكبيرة
            warning = "⚠️" if abs(change_pct) > 30 else ""

            print(f"{key:<20} {base_val:>12.2f} {trained_val:>12.2f} "
                  f"{change:>12.2f} {change_pct:>11.2f}% {warning}")

        print("="*80)

    def visualize_weights(self):
        """رسم مقارنة بصرية للأوزان مع التاريخ"""
        if not self.trained_weights:
            print("❌ No trained weights loaded!")
            return

        from datetime import datetime

        keys = list(self.baseline_weights.keys())
        baseline_vals = [self.baseline_weights[k] for k in keys]
        trained_vals = [self.trained_weights.get(
            k, self.baseline_weights[k]) for k in keys]

        x = np.arange(len(keys))
        width = 0.35

        # إنشاء شكل أكبر بتخطيط محسّن
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

        # ========== الرسم 1: مقارنة القيم ==========
        ax1 = fig.add_subplot(gs[0, :])

        bars1 = ax1.bar(x - width/2, baseline_vals, width,
                        label='Baseline', alpha=0.8, color='#3498db')
        bars2 = ax1.bar(x + width/2, trained_vals, width,
                        label='Trained', alpha=0.8, color='#e74c3c')

        ax1.set_xlabel('Parameters', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Weight Value', fontsize=12, fontweight='bold')
        ax1.set_title('Weight Comparison: Baseline vs Trained',
                      fontsize=14, fontweight='bold', pad=15)
        ax1.set_xticks(x)
        ax1.set_xticklabels(keys, rotation=45, ha='right', fontsize=10)
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.axhline(y=0, color='k', linestyle='-', linewidth=0.5)

        # إضافة قيم فوق الأعمدة
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if abs(height) > 10:
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                             f'{height:.0f}',
                             ha='center', va='bottom' if height > 0 else 'top',
                             fontsize=8, alpha=0.7)

        # ========== الرسم 2: نسبة التغيير ==========
        ax2 = fig.add_subplot(gs[1, 0])

        changes_pct = [(trained_vals[i] - baseline_vals[i]) / baseline_vals[i] * 100
                       if baseline_vals[i] != 0 else 0
                       for i in range(len(keys))]

        colors = ['#27ae60' if c > 0 else '#e74c3c' if c < 0 else '#95a5a6'
                  for c in changes_pct]

        bars = ax2.bar(x, changes_pct, color=colors, alpha=0.7)
        ax2.set_xlabel('Parameters', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Change (%)', fontsize=11, fontweight='bold')
        ax2.set_title('Percentage Change in Weights',
                      fontsize=12, fontweight='bold', pad=10)
        ax2.set_xticks(x)
        ax2.set_xticklabels(keys, rotation=45, ha='right', fontsize=9)
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)

        # خطوط تحذير
        ax2.axhline(y=30, color='orange', linestyle='--', alpha=0.5)
        ax2.axhline(y=-30, color='orange', linestyle='--', alpha=0.5)
        ax2.text(len(keys)-0.5, 32, '±30% threshold',
                 fontsize=8, alpha=0.7, ha='right')

        # إضافة قيم النسب
        for i, (bar, pct) in enumerate(zip(bars, changes_pct)):
            if abs(pct) > 5:  # فقط للتغييرات الكبيرة
                ax2.text(bar.get_x() + bar.get_width()/2., pct,
                         f'{pct:+.1f}%',
                         ha='center', va='bottom' if pct > 0 else 'top',
                         fontsize=7, alpha=0.8, fontweight='bold')

        # ========== الرسم 3: القيم المطلقة للتغيير ==========
        ax3 = fig.add_subplot(gs[1, 1])

        changes_abs = [trained_vals[i] - baseline_vals[i]
                       for i in range(len(keys))]
        colors_abs = ['#27ae60' if c > 0 else '#e74c3c' if c < 0 else '#95a5a6'
                      for c in changes_abs]

        ax3.bar(x, changes_abs, color=colors_abs, alpha=0.7)
        ax3.set_xlabel('Parameters', fontsize=11, fontweight='bold')
        ax3.set_ylabel('Absolute Change', fontsize=11, fontweight='bold')
        ax3.set_title('Absolute Weight Changes',
                      fontsize=12, fontweight='bold', pad=10)
        ax3.set_xticks(x)
        ax3.set_xticklabels(keys, rotation=45, ha='right', fontsize=9)
        ax3.grid(True, alpha=0.3, axis='y')
        ax3.axhline(y=0, color='k', linestyle='-', linewidth=0.5)

        # ========== الرسم 4: Radar Chart للمقارنة ==========
        ax4 = fig.add_subplot(gs[2, :], projection='polar')

        # تطبيع القيم للرسم الرادار
        max_val = max(max(abs(v) for v in baseline_vals),
                      max(abs(v) for v in trained_vals))

        baseline_normalized = [v / max_val for v in baseline_vals]
        trained_normalized = [v / max_val for v in trained_vals]

        # زوايا
        angles = [n / float(len(keys)) * 2 * np.pi for n in range(len(keys))]
        baseline_normalized += baseline_normalized[:1]
        trained_normalized += trained_normalized[:1]
        angles += angles[:1]

        ax4.plot(angles, baseline_normalized, 'o-', linewidth=2,
                 label='Baseline', color='#3498db', alpha=0.8)
        ax4.fill(angles, baseline_normalized, alpha=0.15, color='#3498db')

        ax4.plot(angles, trained_normalized, 'o-', linewidth=2,
                 label='Trained', color='#e74c3c', alpha=0.8)
        ax4.fill(angles, trained_normalized, alpha=0.15, color='#e74c3c')

        ax4.set_xticks(angles[:-1])
        ax4.set_xticklabels(keys, fontsize=9)
        ax4.set_ylim(-1, 1)
        ax4.set_title('Weights Comparison - Radar View',
                      fontsize=12, fontweight='bold', pad=20)
        ax4.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), fontsize=10)
        ax4.grid(True, alpha=0.3)

        # ========== معلومات إضافية ==========
        # حساب إحصائيات
        total_increase = sum(1 for c in changes_pct if c > 0)
        total_decrease = sum(1 for c in changes_pct if c < 0)
        avg_change = np.mean([abs(c) for c in changes_pct])

        info_text = f"""Analysis Summary:
Parameters Increased: {total_increase}/{len(keys)}
Parameters Decreased: {total_decrease}/{len(keys)}
Avg Absolute Change: {avg_change:.1f}%
Max Change: {max(changes_pct):.1f}%
Min Change: {min(changes_pct):.1f}%

Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""

        fig.text(0.02, 0.02, info_text, fontsize=9,
                 family='monospace', verticalalignment='bottom',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # ========== العنوان الرئيسي ==========
        plt.suptitle('Comprehensive Weights Analysis - Senet AI',
                     fontsize=16, fontweight='bold', y=0.995)

        # ========== حفظ ==========
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'weights_analysis_{timestamp}.png'

        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 Visualization saved: {filename}")

        # نسخة سريعة
        plt.savefig('weights_analysis_latest.png',
                    dpi=300, bbox_inches='tight')
        print(f"📊 Latest copy saved: weights_analysis_latest.png")

        plt.show()

    def tournament_test(self, num_games=50):
        """اختبار شامل: مقارنة الأداء"""
        if not self.trained_weights:
            print("❌ No trained weights loaded!")
            return

        print("\n" + "="*80)
        print(f"TOURNAMENT TEST: {num_games} games")
        print("="*80)

        results = {
            'trained_wins': 0,
            'baseline_wins': 0,
            'draws': 0,
            'trained_moves': [],
            'baseline_moves': []
        }

        for game_num in range(num_games):
            print(f"Game {game_num + 1}/{num_games}...", end='\r')

            # لعب مباراة: مدرب vs أساسي
            winner, moves = self._play_game(
                AI('X', depth=3, weights=self.trained_weights),
                AI('O', depth=3, weights=self.baseline_weights)
            )

            if winner == 'X':
                results['trained_wins'] += 1
                results['trained_moves'].append(moves)
            elif winner == 'O':
                results['baseline_wins'] += 1
                results['baseline_moves'].append(moves)
            else:
                results['draws'] += 1

        print()  # سطر جديد

        # النتائج
        print(f"\nResults:")
        print(
            f"  Trained AI wins:   {results['trained_wins']} ({results['trained_wins']/num_games*100:.1f}%)")
        print(
            f"  Baseline AI wins:  {results['baseline_wins']} ({results['baseline_wins']/num_games*100:.1f}%)")
        print(
            f"  Draws:             {results['draws']} ({results['draws']/num_games*100:.1f}%)")

        if results['trained_moves']:
            avg_trained = np.mean(results['trained_moves'])
            print(f"\n  Avg moves (trained wins): {avg_trained:.1f}")

        if results['baseline_moves']:
            avg_baseline = np.mean(results['baseline_moves'])
            print(f"  Avg moves (baseline wins): {avg_baseline:.1f}")

        # تقييم الأداء
        improvement = (results['trained_wins'] -
                       results['baseline_wins']) / num_games * 100
        print(f"\n  Performance improvement: {improvement:+.1f}%")

        if improvement > 10:
            print("  ✅ Excellent! Trained AI significantly better")
        elif improvement > 0:
            print("  ✅ Good! Trained AI is better")
        elif improvement > -10:
            print("  ⚠️  Similar performance")
        else:
            print("  ❌ Warning! Trained AI is worse")

        print("="*80)

        return results

    def _play_game(self, ai_x, ai_o, max_moves=200):
        """لعب مباراة واحدة"""
        board = create_initial_board()
        current_player = 'X'
        move_count = 0

        while move_count < max_moves:
            roll = throw_sticks()

            if current_player == 'X':
                state = GameState.from_board(board, 'X')
                move = ai_x.choose_best_move(state, roll)
            else:
                state = GameState.from_board(board, 'O')
                move = ai_o.choose_best_move(state, roll)

            if move:
                board = apply_move(board, move[0], move[1])

                if check_win(board, current_player):
                    return current_player, move_count

            current_player = 'O' if current_player == 'X' else 'X'
            move_count += 1

        # تعادل
        return 'DRAW', move_count

    def analyze_specific_weights(self):
        """تحليل مفصل لأوزان محددة"""
        if not self.trained_weights:
            print("❌ No trained weights loaded!")
            return

        print("\n" + "="*80)
        print("DETAILED WEIGHT ANALYSIS")
        print("="*80)

        analyses = {
            'piece_off': {
                'description': 'Importance of bearing off pieces',
                'expected': 'High positive (goal of the game)',
                'concern_threshold': 1000
            },
            'progress': {
                'description': 'Value of advancing pieces',
                'expected': 'Moderate positive',
                'concern_threshold': 50
            },
            'happiness': {
                'description': 'Value of House of Happiness',
                'expected': 'Moderate positive',
                'concern_threshold': 50
            },
            'water': {
                'description': 'Penalty for House of Water',
                'expected': 'Negative (danger)',
                'concern_threshold': -150
            },
            'attack': {
                'description': 'Value of attacking opponent',
                'expected': 'Moderate positive',
                'concern_threshold': 30
            },
            'protection': {
                'description': 'Value of protecting pieces',
                'expected': 'Moderate positive',
                'concern_threshold': 20
            }
        }

        for key, info in analyses.items():
            if key not in self.trained_weights:
                continue

            trained_val = self.trained_weights[key]
            base_val = self.baseline_weights[key]

            print(f"\n{key.upper()}")
            print(f"  Description: {info['description']}")
            print(f"  Expected: {info['expected']}")
            print(f"  Baseline: {base_val:.2f}")
            print(f"  Trained: {trained_val:.2f}")

            # تقييم
            if key == 'water':
                # سالب = جيد
                if trained_val < info['concern_threshold']:
                    print(f"  ✅ Good: Strong penalty")
                elif trained_val < base_val:
                    print(f"  ✅ OK: Increased penalty")
                else:
                    print(f"  ⚠️  Warning: Penalty decreased")
            else:
                # موجب = جيد
                if trained_val > info['concern_threshold']:
                    print(f"  ✅ Good: Strong value")
                elif trained_val > base_val:
                    print(f"  ✅ OK: Value increased")
                else:
                    print(f"  ⚠️  Warning: Value decreased")

        print("\n" + "="*80)

    def run_full_analysis(self):
        """تشغيل التحليل الكامل"""
        print("\n" + "🔍" * 40)
        print(" " * 25 + "FULL ANALYSIS")
        print("🔍" * 40)

        # 1. مقارنة الأوزان
        self.compare_weights()

        # 2. تحليل مفصل
        self.analyze_specific_weights()

        # 3. رسم بياني
        self.visualize_weights()

        # 4. اختبار الأداء
        results = self.tournament_test(num_games=30)

        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)

        return results


def main():
    """البرنامج الرئيسي"""
    analyzer = WeightsAnalyzer()

    # تحميل الأوزان المدربة
    if not analyzer.load_trained_weights():
        print("\nTrying alternative filename...")
        if not analyzer.load_trained_weights("best_ai_weights_improved.json"):
            print("❌ Could not load any trained weights!")
            return

    # تشغيل التحليل
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()
