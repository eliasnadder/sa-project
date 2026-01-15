"""
نص تنفيذ سريع لتدريب وتحليل AI لعبة Senet
يوفر قائمة تفاعلية لكل العمليات
"""

import glob
import os
import sys
import json
from datetime import datetime
import trainer_improved
from AI.analyzer import WeightsAnalyzer
from AI.comparison_visualizer import TrainingComparator
import shutil


def print_header():
    """طباعة رأس البرنامج"""
    print("\n" + "="*70)
    print(" " * 15 + "🎮 Senet AI Training & Analysis Suite 🎮")
    print("="*70)
    print()


def print_menu():
    """طباعة القائمة الرئيسية"""
    print("\n" + "-"*70)
    print("📋 Main Menu:")
    print("-"*70)
    print("1️⃣  Analyze Current Weights        - تحليل الأوزان الحالية")
    print("2️⃣  Train AI (Quick)              - تدريب سريع (30 دقيقة)")
    print("3️⃣  Train AI (Standard)           - تدريب قياسي (2-3 ساعات)")
    print("4️⃣  Train AI (Intensive)          - تدريب مكثف (4-6 ساعات)")
    print("5️⃣  Compare Training Sessions     - مقارنة جلسات التدريب")
    print("6️⃣  View Training History         - عرض تاريخ التدريب")
    print("7️⃣  Backup Current Weights        - نسخ احتياطي للأوزان")
    print("8️⃣  Restore Backup Weights        - استعادة نسخة احتياطية")
    print("9️⃣  Test AI Performance           - اختبار أداء الـ AI")
    print("0️⃣  Exit                          - خروج")
    print("-"*70)


def analyze_weights():
    """تحليل الأوزان الحالية"""
    print("\n" + "="*70)
    print("🔍 Analyzing Current Weights...")
    print("="*70)

    try:
        analyzer = WeightsAnalyzer()

        # محاولة تحميل الأوزان
        if not analyzer.load_trained_weights("best_ai_weights.json"):
            if not analyzer.load_trained_weights("best_ai_weights_improved.json"):
                print("\n❌ No weights file found!")
                print("Please train the AI first (option 2, 3, or 4)")
                return

        # تشغيل التحليل
        analyzer.run_full_analysis()

        print("\n✅ Analysis complete!")

    except ImportError as e:
        print(f"\n❌ Error: {e}")
        print("Make sure analyzer.py is in the same directory")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


def train_ai(mode='standard'):
    """تدريب الـ AI"""
    configs = {
        'quick': {
            'POP_SIZE': 15,
            'GENS': 20,
            'MATCHES_PER_EVAL': 10,
            'time_estimate': '30 minutes'
        },
        'standard': {
            'POP_SIZE': 30,
            'GENS': 50,
            'MATCHES_PER_EVAL': 20,
            'time_estimate': '2-3 hours'
        },
        'intensive': {
            'POP_SIZE': 50,
            'GENS': 100,
            'MATCHES_PER_EVAL': 30,
            'time_estimate': '4-6 hours'
        }
    }

    config = configs[mode]

    print("\n" + "="*70)
    print(f"🧬 Training AI - {mode.upper()} Mode")
    print("="*70)
    print(f"\nConfiguration:")
    print(f"  Population Size: {config['POP_SIZE']}")
    print(f"  Generations: {config['GENS']}")
    print(f"  Matches per Evaluation: {config['MATCHES_PER_EVAL']}")
    print(f"  Estimated Time: {config['time_estimate']}")

    # تأكيد
    confirm = input(
        "\n⚠️  This will take a while. Continue? (yes/no): ").lower()
    if confirm not in ['yes', 'y']:
        print("Training cancelled.")
        return

    try:
        # تعديل الإعدادات ديناميكياً
        trainer_improved.POP_SIZE = config['POP_SIZE']
        trainer_improved.GENS = config['GENS']
        trainer_improved.MATCHES_PER_EVAL = config['MATCHES_PER_EVAL']

        # تشغيل التدريب
        trainer = trainer_improved.ImprovedTrainer()
        trainer.run()

        print("\n✅ Training complete!")
        print("\nGenerated files:")
        print("  - best_ai_weights_improved.json")
        print("  - training_stats.json")
        print("  - training_progress_TIMESTAMP.png")

    except ImportError as e:
        print(f"\n❌ Error: {e}")
        print("Make sure trainer_improved.py is in the same directory")
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user!")
        print("Partial results may have been saved.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


def compare_sessions():
    """مقارنة جلسات التدريب"""
    print("\n" + "="*70)
    print("📊 Comparing Training Sessions...")
    print("="*70)

    try:
        comparator = TrainingComparator()

        if not comparator.load_all_training_sessions():
            print("\n❌ No training sessions found!")
            print("Train the AI first to generate comparison data.")
            return

        comparator.create_comprehensive_comparison()

        if len(comparator.training_sessions) >= 2:
            comparator.create_side_by_side_comparison()

        print("\n✅ Comparison complete!")

    except ImportError as e:
        print(f"\n❌ Error: {e}")
        print("Make sure comparison_visualizer.py is in the same directory")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


def view_history():
    """عرض تاريخ التدريب"""
    print("\n" + "="*70)
    print("📚 Training History")
    print("="*70)

    # البحث عن جلسات التدريب
    backup_dir = "backups"

    if not os.path.exists(backup_dir):
        print("\n❌ No backup directory found!")
        print("Train the AI to generate history.")
        return

    # قراءة الملفات
    stats_files = glob.glob(f"{backup_dir}/stats_*.json")

    if not stats_files:
        print("\n❌ No training history found!")
        return

    stats_files.sort(reverse=True)  # الأحدث أولاً

    print(f"\nFound {len(stats_files)} training session(s):\n")

    for i, file in enumerate(stats_files, 1):
        try:
            with open(file, 'r') as f:
                data = json.load(f)

            # استخراج التاريخ
            timestamp = os.path.basename(file).split('_')[1].split('.')[0]
            date_str = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]} " \
                f"{timestamp[9:11]}:{timestamp[11:13]}"

            # عرض المعلومات
            best_score = data.get('final_score', 'N/A')
            generations = len(data.get('best_scores', []))

            print(f"{i}. {date_str}")
            print(f"   Best Score: {best_score}")
            print(f"   Generations: {generations}")
            print()

        except Exception as e:
            print(f"{i}. {os.path.basename(file)} - Error reading file")
            print()


def backup_weights():
    """نسخ احتياطي للأوزان الحالية"""
    print("\n" + "="*70)
    print("💾 Backing Up Current Weights...")
    print("="*70)

    # إنشاء مجلد backups
    os.makedirs("backups", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    files_to_backup = [
        "best_ai_weights.json",
        "best_ai_weights_improved.json",
        "training_stats.json"
    ]

    backed_up = []

    for file in files_to_backup:
        if os.path.exists(file):
            backup_name = f"backups/{file.replace('.json', '')}_{timestamp}.json"

            try:
                shutil.copy2(file, backup_name)
                backed_up.append(backup_name)
                print(f"✅ Backed up: {backup_name}")
            except Exception as e:
                print(f"❌ Error backing up {file}: {e}")

    if backed_up:
        print(f"\n✅ Backup complete! {len(backed_up)} file(s) backed up.")
    else:
        print("\n⚠️  No files found to backup!")


def restore_backup():
    """استعادة نسخة احتياطية"""
    print("\n" + "="*70)
    print("♻️  Restore Backup Weights")
    print("="*70)

    backup_dir = "backups"

    if not os.path.exists(backup_dir):
        print("\n❌ No backup directory found!")
        return

    # قراءة ملفات الأوزان
    weight_files = glob.glob(f"{backup_dir}/weights_*.json")
    weight_files += glob.glob(f"{backup_dir}/best_ai_weights*_*.json")

    if not weight_files:
        print("\n❌ No backup weights found!")
        return

    weight_files.sort(reverse=True)  # الأحدث أولاً

    print("\nAvailable backups:\n")

    for i, file in enumerate(weight_files[:10], 1):  # عرض أحدث 10
        timestamp = os.path.basename(file).split('_')[-1].replace('.json', '')
        if len(timestamp) >= 15:
            date_str = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]} " \
                f"{timestamp[9:11]}:{timestamp[11:13]}"
        else:
            date_str = "Unknown date"

        print(f"{i}. {os.path.basename(file)}")
        print(f"   Date: {date_str}")
        print()

    # اختيار
    try:
        choice = int(input("Select backup to restore (number): "))
        if 1 <= choice <= len(weight_files[:10]):
            selected_file = weight_files[choice - 1]

            # نسخ
            shutil.copy2(selected_file, "best_ai_weights.json")

            print(f"\n✅ Restored: {os.path.basename(selected_file)}")
            print("   → best_ai_weights.json")
        else:
            print("\n❌ Invalid choice!")
    except ValueError:
        print("\n❌ Invalid input!")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def test_performance():
    """اختبار أداء الـ AI"""
    print("\n" + "="*70)
    print("🎯 Testing AI Performance...")
    print("="*70)

    try:
        analyzer = WeightsAnalyzer()

        # تحميل الأوزان
        if not analyzer.load_trained_weights("best_ai_weights.json"):
            if not analyzer.load_trained_weights("best_ai_weights_improved.json"):
                print("\n❌ No weights file found!")
                return

        # اختيار عدد المباريات
        print("\nHow many test games?")
        print("1. Quick test (10 games)")
        print("2. Standard test (30 games)")
        print("3. Thorough test (50 games)")

        choice = input("\nChoice (1-3): ")

        games_map = {'1': 10, '2': 30, '3': 50}
        num_games = games_map.get(choice, 30)

        print(f"\nRunning {num_games} test games...")
        results = analyzer.tournament_test(num_games)

        print("\n✅ Testing complete!")

    except ImportError as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


def main():
    """البرنامج الرئيسي"""
    print_header()

    while True:
        print_menu()

        choice = input("\nYour choice: ").strip()

        if choice == '1':
            analyze_weights()

        elif choice == '2':
            train_ai('quick')

        elif choice == '3':
            train_ai('standard')

        elif choice == '4':
            train_ai('intensive')

        elif choice == '5':
            compare_sessions()

        elif choice == '6':
            view_history()

        elif choice == '7':
            backup_weights()

        elif choice == '8':
            restore_backup()

        elif choice == '9':
            test_performance()

        elif choice == '0':
            print("\n" + "="*70)
            print("👋 Thank you for using Senet AI Training Suite!")
            print("="*70)
            print()
            sys.exit(0)

        else:
            print("\n❌ Invalid choice! Please select 0-9.")

        # انتظار للمتابعة
        input("\n\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)
