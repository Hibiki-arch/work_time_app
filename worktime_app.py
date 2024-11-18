import streamlit as st
from snowflake.snowpark.context import get_active_session
from datetime import datetime
from snowflake.snowpark.functions import col
import pytz
import pandas as pd
import json

cnx = st.connection("snowflake")
session = cnx.session

timezone = pytz.timezone('Asia/Tokyo')

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    
# session = get_active_session()

# タイトル
st.title("勤怠管理")

# グローバル変数を使って現在のページを管理
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# ページを切り替える関数
def go_to_page(page_name):
    st.session_state.page = page_name

# 現在の時間を取得
local_time = datetime.now(timezone)
local_date = datetime.today()
# 表示形式変更
official_time = local_time.strftime("%H:%M")
official_date = local_time.strftime("%Y-%m-%d")
show_date = local_time.strftime("%Y年 %m月 %d日")
show_time = local_time.strftime("%H時 %M分")

st.title(show_time)
st.title(show_date)



insert_time_in = f"""INSERT INTO OUTPUT_DB.TEST.TIME_TABLE(checkin,date)
VALUES (
    '{official_time}',
    '{official_date}' 
)"""


insert_time_out = f"""INSERT INTO OUTPUT_DB.TEST.TIME_TABLE(checkout,date)
VALUES (
    '{official_time}',
    '{official_date}'
)"""


insert_time_brake = f"""INSERT INTO OUTPUT_DB.TEST.TIME_TABLE(brakest,date)
VALUES (
    '{official_time}',
    '{official_date}'
)"""

insert_time_brake_done = f"""INSERT INTO OUTPUT_DB.TEST.TIME_TABLE(brakedn,date)
VALUES (
    '{official_time}',
    '{official_date}'
)"""


# user_information変数

sql = f"select * from user limit 20"
data = session.sql(sql).collect()
users_df = pd.DataFrame(data)

json_data = users_df.to_json(orient='records', force_ascii=False)
data2 = json.loads(json_data)

# names = [username["username"] for username in data2["username"]]

# 結果を表示

# st.write(data2)

new_structure = {}

# 元のデータから新しい構造に変換
for user in data2:
    username = user["USERNAME"]
    password = user["PASSWORD"]
    new_structure[username] = {
        "PASSWORD": password
    }



# ホーム画面
if st.session_state.page == 'login':
    if st.button("アカウント登録"):
        go_to_page('submit_account')
    username_input = st.text_input("ユーザー名")
    password_input = st.text_input("パスワード", type="password")

    # 新しい構造を表示
    # st.write(new_structure)
    
    # username = new_structure[username_input]
    password = new_structure[username_input]["PASSWORD"]
    
    # st.write(username)
    # st.write(password)
    
    
    # USERNAME = username
    USERNAME = username_input
    PASSWORD = password


    if st.button("ログイン"):
        if username_input == USERNAME and password_input == PASSWORD:
            st.session_state.logged_in = True
            go_to_page('home')
            st.success("ログイン成功！")
            
        else:
            st.error('パスワード/ユーザー名が異なります')
            go_to_page('login')



# ホーム画面
elif st.session_state.page == 'home':
    time_submit1 = st.button('出勤打刻')
    time_submit2 = st.button('休憩開始')
    time_submit3 = st.button('休憩終了')
    time_submit4 = st.button('退勤打刻')
    
    if time_submit1:
        session.sql(insert_time_in).collect()
        st.success('出勤しました！！働きます！！')
        st.text(f'{show_time}　打刻しました')
        
    if time_submit2:
        session.sql(insert_time_brake).collect()
        st.success('休憩します！！')
        st.text(f'{show_time}　打刻しました')
        
    if time_submit3:
        session.sql(insert_time_brake_done).collect()
        st.success('休憩しました！！')
        st.text(f'{show_time}　打刻しました')

    if time_submit4:
        session.sql(insert_time_out).collect()
        st.success('退勤しました！！おやすみなさい！！')
        st.text(f'{show_time}　打刻しました')
    
    if 'toggle' not in st.session_state:
        st.session_state.toggle = False
    
    # チェックボックスを作成（オン・オフボタンとして使用）
    toggle = st.checkbox("勤怠記録の確認", value=st.session_state.toggle)
    
    # トグルの状態をセッション状態に保存
    st.session_state.toggle = toggle
    
    # 状態に応じたメッセージの表示
    if toggle:
        my_record_data = session.table("OUTPUT_DB.TEST.work_record").select(
        col('日付'),
        col('出勤時刻'),
        col('休憩開始時刻'),
        col('休憩終了時刻'),
        col('退勤時刻')
    )
        st.dataframe(data=my_record_data, 
                 use_container_width=True
                )
    
    if st.button("ログアウト"):
        go_to_page('login')
    # if st.button("設定ページに移動"):
    #     go_to_page('settings')

elif st.session_state.page == 'submit_account':
    st.title("アカウント登録")
    user_sub=st.text_input("登録ユーザー名")
    pass_sub=st.text_input("登録パスワード")

    insert_submit = f"""INSERT INTO OUTPUT_DB.TEST.USER(username,password)
    VALUES (
        '{user_sub}',
        '{pass_sub}'
    )"""

    if st.button("登録"):
        session.sql(insert_submit).collect()
        st.success("登録完了しました")
        go_to_page('login')
        
    if st.button("ログインページへ"):
        go_to_page('login')

        
# # 設定画面
# elif st.session_state.page == 'settings':
#     st.title("設定")
#     st.write("ここではアプリケーションの設定を行います。")
#     if st.button("ログインに戻る"):
#         go_to_page('login')
#     if st.button("データページに移動"):
#         go_to_page('data')
