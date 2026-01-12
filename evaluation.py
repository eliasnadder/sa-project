from board import (
    HOUSE_OF_HAPPINESS, HOUSE_WATER, HOUSE_THREE_TRUTHS,
    HOUSE_RE_ATUM, HOUSE_HORUS, HOUSE_REBIRTH, BOARD_SIZE, OFF_BOARD
)

class Evaluation:
    
    def __init__(self, player):
        
        self.player = player
        self.opponent = 'O' if player == 'X' else 'X'
        
        self.weights ={
            'piece_off': 1000, # القطعة تطلع لبرا
            'progress': 10, # القطعة تتقدم 
            'happiness': 50, 
            'water': -100,
            'special_house': 30,
            'protection': 20, # الحماية
            'block': 50, # الحجب على الخصم
            'attack': 30, # الهجوم على قطع الخصم 
            'defense': -30, # الدفاع
            'flexibility': 5
        }
        
    def evaluate_board(self, board,valid_moves=None):
        
        # التقييم في حالة عنا فوز
        if self._is_terminal(board):
            return self._evaluate_terminal(board)
        
        # التقييم حسب المرحلة 
        game = self._get_game_phase(board)
        self._adjust_weights_for_phase(game)
        
        total_score = 0
        
        # تقييم القطع يلي طلعت 
        total_score += self._evaluate_pieces_off(board)
        
        # تقييم الاحجار حسب تقدمها
        total_score += self._evaluate_progress(board)
        
        # تقييم المربعات الاساسية الموجودة باللعبة 
        total_score += self._evaluate_special_houses(board)
        
        total_score += self._evaluate_protection_block(board)
        
        total_score += self._evaluate_attack_defense(board)
         # عامل المرونة
        if valid_moves:
            total_score += self._evaluate_flexibility(valid_moves)
        
        return total_score
    
    
    def _evaluate_flexibility(self, valid_moves):
      
        score = 0
        for moves in valid_moves.values():
            score += len(moves) * self.weights['flexibility']
        return score
    
    # هون عم نتحقق اذا اللعبة انتهت 
    def _is_terminal(self, board):
        has_player = any(cell == self.player for cell in board)
        has_opp = any(cell == self.opponent for cell in board)
        return not has_player or not has_opp
    
    # تقييم الحالة النهائية
    def _evaluate_terminal(self, board):
        has_player = any(cell == self.player for cell in board)
        has_opp = any(cell == self.opponent for cell in board)
        
        if not has_player: return 1000 # اذا اللاعب طالع كل قطعو نقاط كتيرة 
        elif not has_opp: return -1000 # اذا الخصم طالع كل قطعو خسارة كبيرة
        return 0
    
    # هون عم نحدد مرحلة اللعبة 
    # البداية 1-15
    # المنتصف 16-25
    # النهاية 26-30
    def _get_game_phase(self, board):
        
        player_pos = [i for i, cell in enumerate(board) if cell == self.player]
        opp_pos = [i for i, cell in enumerate(board) if cell == self.opponent]
        
        if not player_pos or not opp_pos: return 'endgame'
        
        max_pos = max(player_pos + opp_pos) # ابعد فطعة شو ما كان للاعب تبعها وين موجودة
        
        if max_pos < 15: return 'opening'
        elif max_pos < 25: return 'midgame'
        else: return 'endgame'
        
    # هي منشان تقييم المراحل 
    # كل مرحل بتركز على شي معين
    def _adjust_weights_for_phase(self, phase):
        
        # بالبداية
        if phase == 'opening':
            self.weights['protection'] = 25 # حماية اللاعب لقطعو عالية
            # عن طريق انو يحط الو قطع متجاورة هي بتكون جدران دفاعية 
            self.weights['block'] = 60 # حجب قطع الخصم عالي
            # عن طريق انو يشكل حواجر ليعرقل حركة الخصم
            self.weights['progress'] = 5 # التقدم بطيء ما بقدم بسرعة لقدام 
            
        # بالمرحلة يلي بكون اكبر تجمع للقطع بالوسط 
        elif phase == 'midgame':
        # الحجب و الحماية ما بصير في تركيز كبير عليهن و لا اهمال كبير
            self.weights['protection'] = 20 # حماية اللاعب لقطعو عادية 
            self.weights['block'] = 40 # حجب اللاعب لقطع الخصم عادية 
            self.weights['progress'] = 10 # منطي تقدم عالي شوي ليبلش يحرك قطعو من مرحلة المنتصف لمرحلة النهاية
            self.weights['attack'] = 35 # الهجوم مفيد بحاول يبدل بين قطعو و قطع الخسم
        
         # بالمرحلة الاخيرة يلي التجمع الكبير للقع اخر شي باللوحة
        else:
            self.weights['piece_off'] = 1500 # انو يطلع القطع هو الشي الاهم
            self.weights['progress'] = 15 # النقدم بصير عالي لحتى يمشي على بيت السعادة
            self.weights['protection'] = 10 # الدفاع بصير مو كتير مهم
            self.weights['block'] = 20 # افي وقت للحواجز انو يطلع قطعو اهم 
        
    # تقييم القطع يلي طلعت لبرا اللوحة
    def _evaluate_pieces_off(self, board):
        
        player_pieces_on = sum(1 for cell in board if cell == self.player)
        opp_pieces_on = sum(1 for cell in board if cell == self.opponent)
        
        player_pieces_off = 7 - player_pieces_on
        opp_pieces_off = 7 - opp_pieces_on
        
        # الفرق بالقطع يلي طلعت لكل قطعة بتطلع 100 نقطة 
        # اذا اللاعب يلي طلع قطعو النتيجة موجبة بينعطى تقييم عالي
        #اذا الخصم النتيجة سالبة و بينعطى تقييم سيء    
        return (player_pieces_off - opp_pieces_off) * self.weights['piece_off']
    
    
    def _evaluate_progress(self, board):
        
        player_score = 0 
        opp_score = 0 
        
        for i, cell in enumerate(board):
            # كل ما كان اللاعب او الخصم الهن قطع ب مواقع متقدمة 
            # هاد الشي بعلي ال score 
            if cell == self.player: player_score += (i + 1)
            elif cell == self.opponent: opp_score += (i + 1)
            
        # الفرق بالتقدم بين اللاعب و الخصم 
        # في حال اللاعب تقدمو اكنر بينعطى تقييم عالي 
        # في حال الخصم بينعطى تقييم سلبي 
        return (player_score - opp_score) * self.weights['progress']
            
            
    def _evaluate_special_houses(self, board):
        
        score = 0 
        
        if board[HOUSE_OF_HAPPINESS] == self.player: score += self.weights['happiness']
        
        # اذا اللاعب كان فيه هاد شي مو منيح و منحط عقوبة 
        if board[HOUSE_WATER] == self.player: score += self.weights['water']
        # اذا الخصم كان عندو هاد الشي منيح و منخفف العقوبة
        elif board[HOUSE_WATER] == self.opponent: score -= self.weights['water']
        
        special_houses = [HOUSE_THREE_TRUTHS, HOUSE_RE_ATUM, HOUSE_HORUS]
        for house in special_houses: 
            if board[house] == self.player:
                score += self.weights['special_house']
                
        return score
    
    def _evaluate_protection_block(self, board):
        
        score = 0 
        
        for i in range(BOARD_SIZE - 1):
            # هون الحماية اللاعب عندو أحجار متجاورة
            # هون التقييم عالي بصير 
            if board[i] == self.player and board[i + 1] == self.player:
                score += self.weights['protection']
            
            # هون اذا الخصم عندو احجار متجاورة
            # هون التقييم بينقص 
            if board[i] == self.opponent and board[i + 1] == self.opponent:
                score -= self.weights['protection']
                
        
        for i in range(BOARD_SIZE - 2):
        # هون الحجب بكون 3 احجار ل اللاعب متتالية 
            if (board[i] == self.player and 
                board[i + 1] == self.player and 
                board[i + 2] == self.player):
                
                score += self.weights['block']
                
        return score
    
    def _evaluate_attack_defense(self, board):
        
        score = 0 
        
        player_pos = [i for i, cell in enumerate(board) if cell == self.player]
        opp_pos = [i for i, cell in enumerate(board) if cell == self.opponent]
        
        # عم ناخد قطعة من اللاعب و قطعة من الخصم 
        # و نحسب المسافة بينهن 
        for playe_pos in player_pos:
            for op_pos in opp_pos:
                
                dis = abs(playe_pos - op_pos)
                
                # كل ما كانت المسافة اقصر فرصة هجوم اقوى
                if 1 <= dis <= 5:
                    # للمسافة الافصل -- 100% من قيمة الهجوم
                    # المساقة جيدة  -- 80% من قيمةالهجوم
                    # المسافة متوسطة -- 60% من قيمة الهجوم
                    # المسافة ضعيفة -- 20% من قيمة الهجوم
                    attack_value = self.weights['attack'] * (6 - dis) / 5
                    score += attack_value
        
        # القطع المعرضة للهجوم        
        for playe_pos in player_pos:
            # القطع يلي بالبداية بأول 10 مربعات اكثر عرضة للهجوم عقوبة كاملة
            if playe_pos < 10:
                defense_value = self.weights['defense'] * 1.0
            
            # القطع بالمنتصف عقوبة متوسطة
            elif playe_pos < 20:
                defense_value = self.weights['defense'] * 0.5
                
            # القطع بالاخير عقوبة قليلة 
            else:
                defense_value = self.weights['defense'] * 0.2
                
            score += defense_value
            
        return score
    
#________________________________________________________

    def evaluate_move(self, board, move, roll):
        
        from_pos, to_pos = move
        
        score = 0 
        
        # اذا كانت الحركة انو القطعة تطلع لبرا
        if to_pos == OFF_BOARD: score += self.weights['piece_off']
            
        else: 
        # اذا كان الحجر قبل بيت السعادة بخانة وحدة
            if to_pos == HOUSE_OF_HAPPINESS -1: score += 70 
        
        # اذا كان ببيت السعادة و اخد حركتين (يعني على بيت 3 حقائق)
        # او 3 حركات (على بيت التوأمين)
            elif from_pos == HOUSE_OF_HAPPINESS and roll in [2,3]: score += 20
        
        # اذا كان ببيت السعادة و اخد حركة على بيت الماء هون عقوبة
            elif from_pos == HOUSE_OF_HAPPINESS and roll == 1: score += -50
            
        # اذا كان ببيت السعادة مع 4 حركات بيوصل على بين حورس 
            elif from_pos == HOUSE_OF_HAPPINESS and roll == 4: score += 90
            
        # اذا كان ببيت السعادة و 5 حركات بيطلع الحجر لبرا
            elif from_pos == HOUSE_OF_HAPPINESS and roll == 5: score += 100
            
    # اذا كان اللاعب بدو يهجم على قطعة الخسم
        if to_pos != OFF_BOARD and board[to_pos] == self.opponent: score += 30
        
    # يعني اذا القطعة بموقع فيه الخصم يهاجمو بشكل قوي 
    # يعتي اذا القطعة رح تروح لمربع قبل ال 25 هيي معرضة للهجوم 
    # لهيك تعاقب 
        if to_pos < BOARD_SIZE - 5: score -=30 
        
        return score

    
        