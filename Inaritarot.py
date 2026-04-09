import streamlit as st
import time
import random
import base64
from datetime import datetime

# --- デッキの定義 ---
major_arcana = [
    "0 The Fool (愚者)", "1 The Magician (魔術師)", "2 The High Priestess (女教皇)",
    "3 The Empress (女帝)", "4 The Emperor (皇帝)", "5 The Hierophant (法王)",
    "6 The Lovers (恋人)", "7 The Chariot (戦車)", "8 Strength (力)",
    "9 The Hermit (隠者)", "10 Wheel of Fortune (運命の輪)", "11 Justice (正義)",
    "12 The Hanged Man (吊るされた男)", "13 Death (死神)", "14 Temperance (節制)",
    "15 The Devil (悪魔)", "16 The Tower (塔)", "17 The Star (星)",
    "18 The Moon (月)", "19 The Sun (太陽)", "20 Judgement (審判)",
    "21 The World (世界)"
]

suits = ["Wands (杖)", "Cups (聖杯)", "Swords (剣)", "Pentacles (金貨)"]
ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Page", "Knight", "Queen", "King"]
minor_arcana = [f"{rank} of {suit}" for suit in suits for rank in ranks]

full_deck = major_arcana + minor_arcana

# --- スプレッドの役割定義 ---
SPREAD_LABELS = {
    1: ["今のあなたへのメッセージ"],
    3: ["過去", "現在", "未来"],
    6: ["現状", "障害", "過去", "近未来", "本人の深層", "結論・助言"],
    8: ["現状", "障害", "理想", "原因", "過去", "近未来", "助言", "最終結果"]
}

# --- セッション状態の初期化 ---
def init_session_state():
    for key, default in [
        ('deck', list(full_deck)),
        ('main_cards', []),
        ('clarifier_cards', {i: [] for i in range(8)}),
        ('ritual_complete', False),
        ('shuffles', 7),
        ('current_question', ""),
        ('previous_reading', None),
        ('agreed', False),
        ('use_reversed', "正逆あり"),
        ('num_cards', 3) # デフォルトは3枚引き
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

init_session_state()

# --- カードを1枚引く内部ロジック (7枚送りルール適用) ---
def draw_card_logic():
    if len(st.session_state.deck) < 1:
        return None
    
    # 7枚を山札の下へ移動
    for _ in range(7):
        st.session_state.deck.append(st.session_state.deck.pop(0))
    
    # 1枚引く
    card = st.session_state.deck.pop(0)
    
    # 逆位置の判定
    if st.session_state.use_reversed == "正位置のみ":
        position = "正位置"
    else:
        position = random.choice(["正位置", "逆位置"])
    
    return f"{card} 【{position}】"

# --- 機能追加：メモリ管理 ---
def reset_for_new_reading():
    if st.session_state.main_cards:
        st.session_state.previous_reading = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": st.session_state.current_question,
            "use_reversed": st.session_state.use_reversed,
            "num_cards": st.session_state.num_cards,
            "cards": list(st.session_state.main_cards),
            "clarifiers": {k: list(v) for k, v in st.session_state.clarifier_cards.items()}
        }
    st.session_state.deck = list(full_deck)
    st.session_state.main_cards = []
    st.session_state.clarifier_cards = {i: [] for i in range(8)}
    st.session_state.ritual_complete = False

def hard_reset():
    agreed_temp = st.session_state.get('agreed', False)
    previous_temp = st.session_state.get('previous_reading', None)
    st.session_state.clear()
    init_session_state()
    st.session_state.agreed = agreed_temp
    st.session_state.previous_reading = previous_temp

# --- カスタムCSS ---
st.markdown("""
    <style>
    .stApp { background: #1a1a2e; color: #e94560; }
    .stButton>button { color: #e94560; background-color: #1a1a2e; border: 2px solid #e94560; border-radius: 10px; width: 100%; font-size: 1.1em; font-weight: bold; }
    .card-box { 
        background: #ffffff; border-radius: 10px; color: #111; 
        text-align: center; padding: 20px 15px; margin-bottom: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5); font-weight: bold; font-size: 1.1em; line-height: 1.4;
    }
    .role-label { color: #e94560; font-size: 0.85em; margin-bottom: 5px; display: block; }
    .clarifier-box {
        background: #f8f9fa; border-radius: 8px; color: #333;
        text-align: center; padding: 12px; margin-top: 8px; font-size: 0.9em; border: 1px solid #ccc;
    }
    .deck-container { display: flex; justify-content: center; margin-bottom: 15px; margin-top: 15px; }
    .deck-image { width: 180px; border-radius: 12px; box-shadow: 0 6px 12px rgba(0,0,0,0.7); }
    textarea::placeholder, input::placeholder { color: white !important; opacity: 0.8 !important; }
    div[data-testid="stRadio"] label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("神代の稲荷タロット🦊")

# 1. 画像のアップロード
st.markdown("### 🦊 タリスマンの準備")
uploaded_file = st.file_uploader("背面に使うオリジナルアートを選んでください", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    card_back_base64 = base64.b64encode(uploaded_file.read()).decode()
else:
    card_back_base64 = None

st.markdown("---")

# 2. 誓いと儀式の設定
if not st.session_state.agreed:
    st.markdown("### 🐦‍🔥 誓い")
    st.markdown("<div style='background: rgba(233, 69, 96, 0.1); border: 1px solid #e94560; padding: 20px; border-radius: 10px; text-align: center;'><h4>このタロットは世のため人のために使いますか？</h4></div>", unsafe_allow_html=True)
    if st.button("はい、同意します"):
        st.session_state.agreed = True
        st.rerun()
else:
    st.success("誓いは立てられました。門は開かれています。")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ 全てリセット"):
            hard_reset()
            st.rerun()
            
    st.markdown("### 🧪 儀式の設定")
    question_input = st.text_area("占いたい質問内容を入力してください", value=st.session_state.current_question)
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.session_state.num_cards = st.radio("スプレッド選択", [1, 3, 6, 8], index=[1, 3, 6, 8].index(st.session_state.num_cards), horizontal=True)
    with col_s2:
        st.session_state.use_reversed = st.radio("カードの向き", ["正逆あり", "正位置のみ"], horizontal=True)
    
    st.session_state.shuffles = st.number_input("シャッフル時間 (秒)", min_value=1, max_value=99, value=st.session_state.shuffles)

    if st.button("🚪 ノック（一括展開を開始します）"):
        reset_for_new_reading()
        st.session_state.current_question = question_input 
        
        # シャッフルアニメーション
        total = st.session_state.shuffles
        progress_bar = st.progress(0)
        status_text = st.empty()
        for i in range(total):
            status_text.markdown(f"**🔄 心を落ち着けています... 残り {total - i} 秒**")
            random.shuffle(st.session_state.deck)
            time.sleep(1)
            progress_bar.progress(int((i + 1) / total * 100))
        
        # 自動一括ドロー
        status_text.markdown("**✨ カードを展開中...**")
        for _ in range(st.session_state.num_cards):
            card = draw_card_logic()
            st.session_state.main_cards.append(card)
            time.sleep(0.3) # 少し演出
            
        status_text.empty()
        progress_bar.empty()
        st.session_state.ritual_complete = True
        st.rerun()

# 3. カード展開と結果の表示
if st.session_state.ritual_complete:
    st.markdown("### 📖 リーディング")
    
    if card_back_base64:
        st.markdown(f'<div class="deck-container"><img src="data:image/png;base64,{card_back_base64}" class="deck-image"></div>', unsafe_allow_html=True)
    
    # メインカード表示
    labels = SPREAD_LABELS.get(st.session_state.num_cards, [])
    
    # 4列ずつ表示
    for row_start in range(0, len(st.session_state.main_cards), 4):
        cols = st.columns(4)
        for j in range(4):
            idx = row_start + j
            if idx < len(st.session_state.main_cards):
                with cols[j]:
                    label_text = labels[idx] if idx < len(labels) else f"{idx+1}枚目"
                    st.markdown(f"<div class='card-box'><span class='role-label'>【{label_text}】</span>{st.session_state.main_cards[idx]}</div>", unsafe_allow_html=True)
                    
                    # 補足カード表示
                    for c_idx, clarifier in enumerate(st.session_state.clarifier_cards[idx]):
                        st.markdown(f"<div class='clarifier-box'>補足{c_idx+1}: {clarifier}</div>", unsafe_allow_html=True)
                    
                    # 補足ボタン (最大3枚まで)
                    if len(st.session_state.clarifier_cards[idx]) < 3:
                        if st.button(f"➕ 補足を引く", key=f"add_c_{idx}"):
                            drawn = draw_card_logic()
                            if drawn:
                                st.session_state.clarifier_cards[idx].append(drawn)
                                st.rerun()

    st.markdown("---")
    
    # 4. コピー機能
    st.markdown("### 📋 結果をコピー")
    result_text = f"【質問内容】\n{st.session_state.current_question}\n\n"
    result_text += f"【カードの向き設定】\n{st.session_state.use_reversed}\n\n"
    result_text += "【リーディング結果】\n"
    
    for i, card in enumerate(st.session_state.main_cards):
        label_text = labels[i] if i < len(labels) else f"{i+1}枚目"
        result_text += f"[{i+1}枚目: {label_text}] {card}\n"
        for c in st.session_state.clarifier_cards[i]:
            result_text += f"  └ 補足: {c}\n"
    
    result_text += "\nそれぞれの解釈を表にしてまとめて。"
    st.code(result_text, language="text")

# 5. バックアップ表示
if st.session_state.previous_reading:
    with st.expander("📜 1個前の結果 (バックアップ)"):
        prev = st.session_state.previous_reading
        st.write(f"引いた時間: {prev['timestamp']}")
        prev_labels = SPREAD_LABELS.get(prev['num_cards'], [])
        p_text = f"【質問内容】\n{prev['question']}\n\n"
        p_text += f"【カードの向き設定】\n{prev['use_reversed']}\n\n"
        p_text += "【リーディング結果】\n"
        for i, card in enumerate(prev['cards']):
            l_text = prev_labels[i] if i < len(prev_labels) else f"{i+1}枚目"
            p_text += f"[{i+1}枚目: {l_text}] {card}\n"
            for c in prev['clarifiers'].get(i, []):
                p_text += f"  └ 補足: {c}\n"
        p_text += "\nそれぞれの解釈を表にしてまとめて。"
        st.code(p_text, language="text")