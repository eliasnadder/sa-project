import random

def throw_sticks():
    """
    رمي العصي الأربعة في لعبة Senet باستخدام الاحتمالات الدقيقة مباشرة.
    
    Returns:
        int: النتيجة (1، 2، 3، 4، أو 5)
    """
    # النتائج الممكنة
    rolls = [1, 2, 3, 4, 5]
    # الاحتمالات المقابلة لكل نتيجة
    weights = [0.25, 0.375, 0.25, 0.0625, 0.0625]
    
    # اختيار نتيجة واحدة موزونة
    return random.choices(rolls, weights=weights, k=1)[0]
