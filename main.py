import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption(
    "1년치(365일) 일별 박스오피스 Top 10 데이터를 활용한 시계열 데이터 시각화 도감입니다."
)


# [데이터 불러오기 및 전처리] 캐시를 적용하여 매번 새로 고침 시 다운로드하지 않도록 함
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    # CSV 데이터 불러오기
    df = pd.read_csv(url)

    # 컬럼명 매핑 (원본 데이터 형식 대응)
    # 데이터셋 헤더: 날짜, 순위, 영화코드, 영화명, 일관객, 누적관객, 스크린수, 상영횟수
    # 날짜 열을 YYYYMMDD 형태의 문자열에서 datetime 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")

    # 수치형 데이터 변환
    numeric_cols = ["순위", "일관객", "누적관객", "스크린수", "상영횟수"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


# 데이터 로드
try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# -----------------------------------------------------------------------------
# [구역 1] 단일 영화 선택 및 날짜별 일관객 변화
# -----------------------------------------------------------------------------
st.divider()
st.header("📌 Section 1. 개별 영화 추이 분석")

# 영화 목록 추출 (가나다 순 정렬)
movie_list = sorted(df["영화명"].unique())

# 영화 선택 드롭다운
selected_movie = st.selectbox(
    "📊 관객수 추이를 확인할 영화를 선택하세요",
    options=movie_list,
    index=0 if movie_list else None,
)

if selected_movie:
    # 선택된 영화의 데이터 필터링 및 날짜순 정렬
    movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

    # Plotly 선 그래프(Line Chart) 생성
    fig1 = px.line(
        movie_df,
        x="날짜",
        y="일관객",
        title=f"<b>[{selected_movie}]</b> 날짜별 일관객수 변화",
        labels={"날짜": "날짜", "일관객": "일일 관객수 (명)"},
        markers=True,  # 데이터 지점에 마커 표시
    )

    # 마우스 오버(Hover) 시 나타날 정보 설정
    fig1.update_traces(
        hovertemplate="<b>날짜</b>: %{x|%Y년 %m월 %d일}<br><b>일관객</b>: %{y:,}명<extra></extra>",
        line=dict(width=2.5, color="#E50914"),  # 선 두께 및 색상 설정
        marker=dict(size=6),
    )

    # 레이아웃 미세 조정
    fig1.update_layout(
        hovermode="x unified",
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0", tickformat=","),
        margin=dict(l=40, r=40, t=60, b=40),
    )

    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig1, use_container_width=True)

    # 그래프 해설/인사이트
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** "
        f"'{selected_movie}'의 개봉 초기 관객 집중도, 주말/평일 관객 유입 차이, 그리고 흥행의 지속성을 시간 흐름에 따라 한눈에 파악할 수 있습니다."
    )


# -----------------------------------------------------------------------------
# [구역 2] 일관객 합계 Top 5 영화 관객 추이 비교
# -----------------------------------------------------------------------------
st.divider()
st.header("📌 Section 2. 일관객 합계 Top 5 영화 관객 추이 비교")

# 1. 이 기간 일관객 합계가 가장 큰 영화 상위 5편 추출
top5_movies = (
    df.groupby("영화명")["일관객"]
    .sum()
    .nlargest(5)
    .index.tolist()
)

# 2. Top 5 영화 데이터 필터링 및 날짜순 정렬
top5_df = df[df["영화명"].isin(top5_movies)].sort_values(["날짜", "영화명"])

# 3. Plotly 다중 선 그래프 생성 (색상으로 영화 구분)
fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    title="<b>기간 내 일관객 합계 Top 5 영화의 날짜별 관객수 변화 비교</b>",
    labels={"날짜": "날짜", "일관객": "일일 관객수 (명)", "영화명": "영화 제목"},
    markers=True,
)

# 마우스 오버 툴팁 및 범례 설정
fig2.update_traces(
    hovertemplate="<b>영화명</b>: %{fullData.name}<br><b>날짜</b>: %{x|%Y년 %m월 %d일}<br><b>일관객</b>: %{y:,}명<extra></extra>",
    marker=dict(size=5),
)

fig2.update_layout(
    hovermode="x unified",
    xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    yaxis=dict(showgrid=True, gridcolor="#f0f0f0", tickformat=","),
    legend=dict(
        title="영화명 (클릭하여 켜기/끄기)",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    margin=dict(l=40, r=40, t=80, b=40),
)

# Streamlit 화면에 그래프 출력
st.plotly_chart(fig2, use_container_width=True)

# 그래프 해설/인사이트
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "기간 내 가장 많은 관객을 모은 흥행작 5편의 개봉 시기, 최고 흥행 정점(피크)의 높이, 그리고 경쟁 영화 간 상영 기간의 겹침과 흥행 화력 차이를 서로 비교해 볼 수 있습니다."
)


# -----------------------------------------------------------------------------
# [구역 3] 날짜별 박스오피스 10위권 관객수 합계 (영역 그래프)
# -----------------------------------------------------------------------------
st.divider()
st.header("📌 Section 3. 날짜별 Top 10 총 관객수 추이 (전체 시장 규모)")

# 1. 날짜별 10위권 일관객 합계 계산
daily_sum = (
    df.groupby("날짜")["일관객"]
    .sum()
    .reset_index()
    .sort_values("날짜")
)

# 2. 합계가 가장 컸던 날 상위 3일 추출
top3_days = daily_sum.nlargest(3, "일관객")

# 3. Plotly 영역 그래프(Area Chart) 생성
fig3 = px.area(
    daily_sum,
    x="날짜",
    y="일관객",
    title="<b>날짜별 박스오피스 Top 10 일관객 합계 추이</b>",
    labels={"날짜": "날짜", "일관객": "Top 10 관객 합계 (명)"},
)

# 영역 그래프 스타일링
fig3.update_traces(
    line=dict(color="#2E86C1", width=2),
    fillcolor="rgba(46, 134, 193, 0.3)",
    hovertemplate="<b>날짜</b>: %{x|%Y년 %m월 %d일}<br><b>총 관객수</b>: %{y:,}명<extra></extra>",
)

# 4. 상위 3일 지점에 마커 및 주석(Annotation) 추가
for i, row in top3_days.iterrows():
    date_str = row["날짜"].strftime("%Y-%m-%d")
    cnt_str = f"{int(row['일관객']):,}명"

    # 그래프 위에 강조 표시 마커 추가
    fig3.add_trace(
        go.Scatter(
            x=[row["날짜"]],
            y=[row["일관객"]],
            mode="markers",
            marker=dict(size=10, color="red", symbol="circle"),
            name="최고 관객일 Top 3",
            showlegend=False,
            hoverinfo="skip",
        )
    )

    # 텍스트 라벨 추가
    fig3.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=f"<b>{date_str}</b><br>({cnt_str})",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor="red",
        ax=0,
        ay=-45,
        bgcolor="#FFFFFF",
        bordercolor="red",
        borderwidth=1,
        font=dict(size=11, color="black"),
    )

# 레이아웃 미세 조정
fig3.update_layout(
    hovermode="x unified",
    xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    yaxis=dict(showgrid=True, gridcolor="#f0f0f0", tickformat=","),
    margin=dict(l=40, r=40, t=80, b=40),
)

# Streamlit 화면에 그래프 출력
st.plotly_chart(fig3, use_container_width=True)

# 그래프 해설/인사이트
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "전체 영화 시장의 일별 총 관객 흐름과 성수기/비성수기 주기를 파악할 수 있으며, 1년 중 극장에 가장 많은 관객이 몰렸던 피크데이 Top 3 날짜와 관객 규모를 한눈에 확인할 수 있습니다."
)
