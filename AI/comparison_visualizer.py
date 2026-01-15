"""
أداة لإنشاء مقارنات بصرية شاملة بين نتائج التدريب المختلفة
"""
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import glob


class TrainingComparator:
    """مقارنة شاملة لنتائج التدريب"""

    def __init__(self):
        self.training_sessions = []

    def load_all_training_sessions(self):
        """تحميل كل جلسات التدريب من مجلد backups"""
        print("🔍 Searching for training sessions...")

        # تحميل الملفات من backups
        stats_files = glob.glob("backups/stats_*.json")

        if not stats_files:
            print("  ℹ️  No backup training sessions found")
            # محاولة تحميل الملف الأساسي
            if os.path.exists("training_stats.json"):
                self._load_session("training_stats.json", "Current")
        else:
            stats_files.sort()  # ترتيب زمني

            for file in stats_files:
                # استخراج التاريخ من اسم الملف
                timestamp = file.split('_')[1].split(
                    '.')[0]  # stats_TIMESTAMP.json
                date_str = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]} " \
                    f"{timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:15]}"

                self._load_session(file, date_str)

            # تحميل الجلسة الحالية أيضاً
            if os.path.exists("training_stats.json"):
                self._load_session("training_stats.json", "Current Session")

        print(f"  ✅ Loaded {len(self.training_sessions)} training session(s)")
        return len(self.training_sessions) > 0

    def _load_session(self, filename, label):
        """تحميل جلسة تدريب واحدة"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            session = {
                'label': label,
                'filename': filename,
                'data': data
            }

            self.training_sessions.append(session)
            print(f"    📂 {label}")

        except Exception as e:
            print(f"    ❌ Error loading {filename}: {e}")

    def create_comprehensive_comparison(self):
        """إنشاء مقارنة شاملة"""
        if not self.training_sessions:
            print("❌ No training sessions to compare!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'training_comparison_{timestamp}.png'

        # إنشاء الشكل
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3)

        # ========== 1. مقارنة أفضل النقاط ==========
        ax1 = fig.add_subplot(gs[0, :2])
        self._plot_best_scores_comparison(ax1)

        # ========== 2. مقارنة متوسط النقاط ==========
        ax2 = fig.add_subplot(gs[1, :2])
        self._plot_avg_scores_comparison(ax2)

        # ========== 3. مقارنة التنوع ==========
        ax3 = fig.add_subplot(gs[2, :2])
        self._plot_diversity_comparison(ax3)

        # ========== 4. إحصائيات نهائية ==========
        ax4 = fig.add_subplot(gs[0, 2])
        self._plot_final_stats(ax4)

        # ========== 5. مقارنة الأوزان ==========
        ax5 = fig.add_subplot(gs[1:, 2])
        self._plot_weights_heatmap(ax5)

        # ========== العنوان والمعلومات ==========
        plt.suptitle('Comprehensive Training Comparison - All Sessions',
                     fontsize=18, fontweight='bold', y=0.995)

        info_text = f"""Comparison Report
Sessions Analyzed: {len(self.training_sessions)}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""

        fig.text(0.02, 0.02, info_text, fontsize=9,
                 family='monospace', verticalalignment='bottom',
                 bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

        # ========== حفظ ==========
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"\n📊 Comprehensive comparison saved: {filename}")

        # حفظ نسخة سريعة
        plt.savefig('training_comparison_latest.png',
                    dpi=300, bbox_inches='tight')
        print(f"📊 Latest copy saved: training_comparison_latest.png")

        plt.show()

    def _plot_best_scores_comparison(self, ax):
        """رسم مقارنة أفضل النقاط"""
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.training_sessions)))

        for i, session in enumerate(self.training_sessions):
            data = session['data']
            if 'best_scores' in data:
                generations = list(range(1, len(data['best_scores']) + 1))
                ax.plot(generations, data['best_scores'],
                        label=session['label'], linewidth=2.5,
                        color=colors[i], marker='o', markersize=3, alpha=0.8)

        ax.set_xlabel('Generation', fontsize=11, fontweight='bold')
        ax.set_ylabel('Best Score', fontsize=11, fontweight='bold')
        ax.set_title('Best Score Evolution - All Training Sessions',
                     fontsize=12, fontweight='bold', pad=10)
        ax.legend(loc='best', fontsize=8, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim(left=0)

    def _plot_avg_scores_comparison(self, ax):
        """رسم مقارنة متوسط النقاط"""
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.training_sessions)))

        for i, session in enumerate(self.training_sessions):
            data = session['data']
            if 'avg_scores' in data:
                generations = list(range(1, len(data['avg_scores']) + 1))
                ax.plot(generations, data['avg_scores'],
                        label=session['label'], linewidth=2.5,
                        color=colors[i], marker='s', markersize=3, alpha=0.8)

        ax.set_xlabel('Generation', fontsize=11, fontweight='bold')
        ax.set_ylabel('Average Score', fontsize=11, fontweight='bold')
        ax.set_title('Average Score Evolution - All Training Sessions',
                     fontsize=12, fontweight='bold', pad=10)
        ax.legend(loc='best', fontsize=8, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim(left=0)

    def _plot_diversity_comparison(self, ax):
        """رسم مقارنة التنوع"""
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.training_sessions)))

        for i, session in enumerate(self.training_sessions):
            data = session['data']
            if 'diversity' in data:
                generations = list(range(1, len(data['diversity']) + 1))
                ax.plot(generations, data['diversity'],
                        label=session['label'], linewidth=2.5,
                        color=colors[i], marker='^', markersize=3, alpha=0.8)

        ax.set_xlabel('Generation', fontsize=11, fontweight='bold')
        ax.set_ylabel('Diversity Score', fontsize=11, fontweight='bold')
        ax.set_title('Population Diversity - All Training Sessions',
                     fontsize=12, fontweight='bold', pad=10)
        ax.legend(loc='best', fontsize=8, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim(left=0)

    def _plot_final_stats(self, ax):
        """رسم الإحصائيات النهائية"""
        ax.axis('off')

        # جمع الإحصائيات
        stats_text = "📊 Final Statistics\n" + "="*30 + "\n\n"

        for i, session in enumerate(self.training_sessions):
            data = session['data']

            stats_text += f"{i+1}. {session['label']}\n"

            if 'best_scores' in data and data['best_scores']:
                final_best = data['best_scores'][-1]
                stats_text += f"   Best: {final_best:.2f}\n"

            if 'avg_scores' in data and data['avg_scores']:
                final_avg = data['avg_scores'][-1]
                stats_text += f"   Avg:  {final_avg:.2f}\n"

            if 'final_score' in data:
                stats_text += f"   Peak: {data['final_score']:.2f}\n"

            stats_text += "\n"

        # إيجاد الأفضل
        best_session = None
        best_score = -float('inf')

        for session in self.training_sessions:
            data = session['data']
            score = data.get('final_score',
                             data.get('best_scores', [0])[-1] if 'best_scores' in data else 0)
            if score > best_score:
                best_score = score
                best_session = session['label']

        if best_session:
            stats_text += f"🏆 Best Session:\n{best_session}\n"
            stats_text += f"Score: {best_score:.2f}"

        ax.text(0.05, 0.95, stats_text,
                transform=ax.transAxes,
                fontsize=9, family='monospace',
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    def _plot_weights_heatmap(self, ax):
        """رسم خريطة حرارية للأوزان"""
        # جمع الأوزان من كل الجلسات
        all_weights = {}
        session_labels = []

        for session in self.training_sessions:
            data = session['data']
            if 'final_weights' in data:
                session_labels.append(session['label'][:15])  # اختصار الاسم

                for key, value in data['final_weights'].items():
                    if key not in all_weights:
                        all_weights[key] = []
                    all_weights[key].append(value)

        if not all_weights or not session_labels:
            ax.text(0.5, 0.5, 'No weight data available',
                    ha='center', va='center', fontsize=12)
            ax.axis('off')
            return

        # تحويل لمصفوفة
        weight_keys = list(all_weights.keys())
        matrix = np.array([all_weights[k] for k in weight_keys])

        # تطبيع البيانات لكل صف (لرؤية الاختلافات بشكل أفضل)
        matrix_normalized = np.zeros_like(matrix)
        for i in range(len(matrix)):
            row_min = matrix[i].min()
            row_max = matrix[i].max()
            if row_max - row_min > 0:
                matrix_normalized[i] = (
                    matrix[i] - row_min) / (row_max - row_min)
            else:
                matrix_normalized[i] = 0.5

        # رسم الخريطة
        im = ax.imshow(matrix_normalized, cmap='RdYlGn',
                       aspect='auto', vmin=0, vmax=1)

        ax.set_xticks(np.arange(len(session_labels)))
        ax.set_yticks(np.arange(len(weight_keys)))
        ax.set_xticklabels(session_labels, rotation=45, ha='right', fontsize=8)
        ax.set_yticklabels(weight_keys, fontsize=8)

        ax.set_title('Weights Evolution Heatmap\n(Normalized per parameter)',
                     fontsize=11, fontweight='bold', pad=10)

        # إضافة شريط الألوان
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Relative Value', fontsize=8)

        # إضافة القيم على الخلايا
        for i in range(len(weight_keys)):
            for j in range(len(session_labels)):
                text = ax.text(j, i, f'{matrix[i, j]:.0f}',
                               ha="center", va="center",
                               color="black", fontsize=6, alpha=0.7)

    def create_side_by_side_comparison(self, session1_idx=0, session2_idx=-1):
        """مقارنة جنباً إلى جنب لجلستين"""
        if len(self.training_sessions) < 2:
            print("❌ Need at least 2 sessions for side-by-side comparison")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'side_by_side_{timestamp}.png'

        session1 = self.training_sessions[session1_idx]
        session2 = self.training_sessions[session2_idx]

        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle(f'Side-by-Side Comparison\n{session1["label"]} vs {session2["label"]}',
                     fontsize=14, fontweight='bold')

        # مقارنة النقاط
        data1 = session1['data']
        data2 = session2['data']

        if 'best_scores' in data1 and 'best_scores' in data2:
            gen1 = list(range(1, len(data1['best_scores']) + 1))
            gen2 = list(range(1, len(data2['best_scores']) + 1))

            axes[0, 0].plot(gen1, data1['best_scores'], label=session1['label'],
                            linewidth=2, marker='o', markersize=4)
            axes[0, 0].plot(gen2, data2['best_scores'], label=session2['label'],
                            linewidth=2, marker='s', markersize=4)
            axes[0, 0].set_title('Best Scores')
            axes[0, 0].legend()
            axes[0, 0].grid(True, alpha=0.3)

        if 'avg_scores' in data1 and 'avg_scores' in data2:
            axes[0, 1].plot(gen1, data1['avg_scores'], label=session1['label'],
                            linewidth=2, marker='o', markersize=4)
            axes[0, 1].plot(gen2, data2['avg_scores'], label=session2['label'],
                            linewidth=2, marker='s', markersize=4)
            axes[0, 1].set_title('Average Scores')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)

        # مقارنة الأوزان
        if 'final_weights' in data1 and 'final_weights' in data2:
            keys = list(data1['final_weights'].keys())
            vals1 = [data1['final_weights'][k] for k in keys]
            vals2 = [data2['final_weights'][k] for k in keys]

            x = np.arange(len(keys))
            width = 0.35

            axes[1, 0].bar(x - width/2, vals1, width,
                           label=session1['label'], alpha=0.8)
            axes[1, 0].bar(x + width/2, vals2, width,
                           label=session2['label'], alpha=0.8)
            axes[1, 0].set_xticks(x)
            axes[1, 0].set_xticklabels(keys, rotation=45, ha='right')
            axes[1, 0].set_title('Final Weights Comparison')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3, axis='y')

        # الفرق في الأوزان
        if 'final_weights' in data1 and 'final_weights' in data2:
            differences = [vals2[i] - vals1[i] for i in range(len(vals1))]
            colors = ['green' if d > 0 else 'red' for d in differences]

            axes[1, 1].bar(x, differences, color=colors, alpha=0.7)
            axes[1, 1].set_xticks(x)
            axes[1, 1].set_xticklabels(keys, rotation=45, ha='right')
            axes[1, 1].set_title('Weight Differences (Session 2 - Session 1)')
            axes[1, 1].axhline(y=0, color='black',
                               linestyle='-', linewidth=0.5)
            axes[1, 1].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"\n📊 Side-by-side comparison saved: {filename}")
        plt.show()


def main():
    """البرنامج الرئيسي"""
    print("="*60)
    print("Training Sessions Comparator")
    print("="*60)

    comparator = TrainingComparator()

    if not comparator.load_all_training_sessions():
        print("\n❌ No training sessions found to compare!")
        print("Run the trainer first to generate training data.")
        return

    print("\n" + "="*60)
    print("Generating Visualizations...")
    print("="*60)

    # مقارنة شاملة
    comparator.create_comprehensive_comparison()

    # إذا كان هناك أكثر من جلستين، قم بمقارنة جنباً إلى جنب
    if len(comparator.training_sessions) >= 2:
        print("\nGenerating side-by-side comparison...")
        comparator.create_side_by_side_comparison(0, -1)

    print("\n✅ All visualizations complete!")


if __name__ == "__main__":
    main()
