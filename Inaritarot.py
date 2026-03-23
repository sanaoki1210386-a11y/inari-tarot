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

# --- セッション状態の初期化 ---
for key, default in [
    ('deck', list(full_deck)),
    ('main_cards', []),
    ('clarifier_cards', {i: [] for i in range(8)}),
    ('ritual_complete', False),
    ('shuffles', 7),
    ('current_question', ""),
    ('previous_reading', None),
    ('agreed', False)
]:
    if key not in st.session_state:
        st.session_state[key] = default

def reset_for_new_reading():
    if st.session_state.main_cards:
        st.session_state.previous_reading = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "question": st.session_state.current_question,
            "cards": list(st.session_state.main_cards),
            "clarifiers": {k: list(v) for k, v in st.session_state.clarifier_cards.items()}
        }
    st.session_state.deck = list(full_deck)
    st.session_state.main_cards = []
    st.session_state.clarifier_cards = {i: [] for i in range(8)}
    st.session_state.ritual_complete = False
    st.session_state.agreed = False

# --- カスタムCSS ---
st.markdown("""
    <style>
    .stApp { background: #1a1a2e; color: #e94560; }
    .stButton>button { color: #e94560; background-color: #1a1a2e; border: 2px solid #e94560; border-radius: 10px; width: 100%; }
    .card-box { 
        background: #f0f0f0; border-radius: 10px; color: #333; 
        text-align: center; padding: 15px; margin-bottom: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3); font-weight: bold; font-size: 0.9em;
    }
    .clarifier-box {
        background: #dcdcdc; border-radius: 8px; color: #555;
        text-align: center; padding: 10px; margin-top: 5px; font-size: 0.8em;
    }
    .deck-container {
        display: flex; justify-content: center; margin-bottom: 10px; margin-top: 10px;
    }
    .deck-image {
        width: 180px; border-radius: 12px; box-shadow: 0 6px 12px rgba(0,0,0,0.7);
    }
    .pledge-box {
        background: rgba(233, 69, 96, 0.1); border: 1px solid #e94560; 
        padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;
    }
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
st.markdown("### 🐦‍🔥 誓い")

if not st.session_state.agreed:
    st.markdown("<div class='pledge-box'><h4>このタロットは世のため人のために使いますか？</h4></div>", unsafe_allow_html=True)
    if st.button("はい、同意します"):
        st.session_state.agreed = True
        st.rerun()
else:
    st.success("誓いは立てられました。門は開かれています。")
    
    st.markdown("### 🧪 儀式の設定")
    question_input = st.text_area("占いたい質問内容を入力してください", placeholder="例：これからの研究生活について、気をつけるべきことは？")
    st.session_state.shuffles = st.number_input("シャッフル回数 (上限99回)", min_value=1, max_value=99, value=st.session_state.shuffles)

    if st.button("🚪 ノック（質問を想起してください）"):
        agreed_temp = st.session_state.agreed 
        reset_for_new_reading()
        st.session_state.agreed = agreed_temp 
        st.session_state.current_question = question_input 
        
        total = st.session_state.shuffles
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(total):
            status_text.markdown(f"**🔄 心を落ち着けています... 残り {total - i} 秒**")
            random.shuffle(st.session_state.deck)
            time.sleep(1)
            progress_bar.progress(int((i + 1) / total * 100))
            
        status_text.markdown("**✨ 儀式が完了しました。カードを展開する準備ができました。**")
        time.sleep(1) 
        status_text.empty()
        progress_bar.empty()
        st.session_state.ritual_complete = True
        st.rerun()

def animate_and_draw_single(label):
    anim_placeholder = st.empty()
    for i in range(1, 8):
        anim_placeholder.info(f"🔄 {label} : {i}枚目のカードを底へ移動中...")
        time.sleep(0.4) 
    anim_placeholder.empty()

    for _ in range(7):
        if len(st.session_state.deck) > 0:
            st.session_state.deck.append(st.session_state.deck.pop(0))
    
    if len(st.session_state.deck) > 0:
        card = st.session_state.deck.pop(0)
        position = random.choice(["正位置", "逆位置"])
        return f"{card} 【{position}】"
    return None

# 3. カード展開と結果の表示
if st.session_state.ritual_complete:
    st.markdown("### 📖 リーディング")
    
    if card_back_base64:
        st.markdown(f'''
            <div class="deck-container">
                <img src="data:image/png;base64,{card_back_base64}" class="deck-image" alt="Talisman Deck">
            </div>
        ''', unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; color: #aaa; margin-bottom: 20px; font-size: 0.9em;'>タロットマット</div>", unsafe_allow_html=True)
    
    current_drawn_count = len(st.session_state.main_cards)
    if current_drawn_count < 8:
        if st.button(f"✨ {current_drawn_count + 1}枚目のカードを引く"):
            drawn_card = animate_and_draw_single(f"{current_drawn_count + 1}枚目の展開")
            if drawn_card:
                st.session_state.main_cards.append(drawn_card)
                st.rerun()
    else:
        st.success("8枚すべての展開が完了しました！")

    st.markdown("---")
    
    # 👇 ここが修正ポイント！ 4枚ごとに新しい行を作成します
    if st.session_state.main_cards:
        for row_start in range(0, len(st.session_state.main_cards), 4):
            cols = st.columns(4)
            for j in range(4):
                i = row_start + j
                if i < len(st.session_state.main_cards):
                    card = st.session_state.main_cards[i]
                    with cols[j]:
                        st.markdown(f"<div class='card-box'>【{i+1}枚目】<br>{card}</div>", unsafe_allow_html=True)
                        for clarifier in st.session_state.clarifier_cards[i]:
                            st.markdown(f"<div class='clarifier-box'>補足: {clarifier}</div>", unsafe_allow_html=True)
                        
                        if len(st.session_state.clarifier_cards[i]) < 2 and len(st.session_state.deck) > 0:
                            if st.button(f"➕ {i+1}枚目の補足を引く", key=f"add_clarifier_{i}"):
                                drawn = animate_and_draw_single(f"【{i+1}枚目】の補足カード")
                                if drawn:
                                    st.session_state.clarifier_cards[i].append(drawn)
                                    st.rerun()
            # 行の間に余白を追加
            st.write("") 
            st.write("") 

        st.markdown("---")
        
        # 4. コピー機能
        st.markdown("### 📋 結果をコピー")
        result_text = ""
        
        if st.session_state.current_question:
            result_text += f"【質問内容】\n{st.session_state.current_question}\n\n"
            
        result_text += "【リーディング結果】\n"
        for i, card in enumerate(st.session_state.main_cards):
            result_text += f"[{i+1}枚目] {card}\n"
            for c in st.session_state.clarifier_cards[i]:
                 result_text += f"  └ 補足: {c}\n"
        
        result_text += "\nそれぞれの解釈を表にしてまとめて。"
        st.code(result_text, language="text")

# 5. 1つ前のバックアップの表示
if st.session_state.previous_reading:
    st.markdown("---")
    st.markdown("### 📜 1個前の結果 (バックアップ)")
    prev = st.session_state.previous_reading
    st.write(f"引いた時間: {prev['timestamp']}")
    prev_text = ""
    
    if prev.get('question'):
        prev_text += f"【質問内容】\n{prev['question']}\n\n"
        
    prev_text += "【リーディング結果】\n"
    for i, card in enumerate(prev['cards']):
        prev_text += f"[{i+1}枚目] {card}\n"
        for c in prev['clarifiers'].get(i, []):
             prev_text += f"  └ 補足: {c}\n"
             
    prev_text += "\nそれぞれの解釈を表にしてまとめて。"
    st.code(prev_text, language="text")