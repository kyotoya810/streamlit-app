import streamlit as st
import pandas as pd

st.set_page_config(page_title="施設別 月次集計", layout="wide")
st.title("📊 施設別 月次 売上・単価・リードタイム・稼働率 ダッシュボード")

uploaded_file = st.file_uploader("📁 売上CSVファイルをアップロードしてください", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    # 日付・数値の変換
    df['チェックイン'] = pd.to_datetime(df['チェックイン'], errors='coerce')
    df['予約日'] = pd.to_datetime(df['予約日'], errors='coerce')
    df['販売'] = pd.to_numeric(df['販売'], errors='coerce')
    df['合計日数'] = pd.to_numeric(df['合計日数'], errors='coerce')

    # 必要な加工
    df['年月'] = df['チェックイン'].dt.to_period('M')
    df['リードタイム'] = (df['チェックイン'] - df['予約日']).dt.days

    # 集計処理（施設×月）
    summary = df.groupby(['年月', '物件名']).agg(
        売上合計=('販売', 'sum'),
        泊数合計=('合計日数', 'sum'),
        平均宿泊単価=('販売', lambda x: x.sum() / df.loc[x.index, '合計日数'].sum()),
        平均リードタイム=('リードタイム', 'mean')
    ).reset_index()

    # 稼働率（簡易：月30日で固定）
    summary['稼働率（仮）'] = (summary['泊数合計'] / 30 * 100).round(1)

    # 表示用整形
    display_df = summary.copy()
    display_df['売上合計'] = display_df['売上合計'].apply(lambda x: f"{int(x):,} 円")
    display_df['平均宿泊単価'] = display_df['平均宿泊単価'].apply(lambda x: f"{x:,.0f} 円")
    display_df['平均リードタイム'] = display_df['平均リードタイム'].apply(lambda x: f"{x:.1f} 日")
    display_df['稼働率（仮）'] = display_df['稼働率（仮）'].apply(lambda x: f"{x:.1f} %")

    st.subheader("📋 月別 × 施設別 集計結果（縦表示）")
    st.dataframe(display_df)

    # グラフ表示（選択式）
    st.subheader("📈 グラフで可視化")
    metric = st.selectbox("表示する項目を選んでください", ['売上合計', '平均宿泊単価', '平均リードタイム', '稼働率（仮）'])
    metric_data = summary[['年月', '物件名', metric]]

    # グラフ化（物件名ごとに色分け）
    chart_data = metric_data.pivot(index='年月', columns='物件名', values=metric)
    st.line_chart(chart_data)

    # CSVダウンロード
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8-sig')

    csv_data = convert_df(summary)
    st.download_button("⬇ この集計結果をCSVでダウンロード", csv_data, file_name="月次集計_施設別.csv", mime='text/csv')

else:
    st.info("まずはCSVファイルをアップロードしてください。")
