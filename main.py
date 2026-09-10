import pandas as pd
import plotly.express as px
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
# [구역 1] 영화별 날짜별 일관객 변화
# -----------------------------------------------------------------------------
st.divider()
st.header("📌 Section 1. 영화별 추이 분석")

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
    fig = px.line(
        movie_df,
        x="날짜",
        y="일관객",
        title=f"<b>[{selected_movie}]</b> 날짜별 일관객수 변화",
        labels={"날짜": "날짜", "일관객": "일일 관객수 (명)"},
        markers=True,  # 데이터 지점에 마커 표시
    )

    # 마우스 오버(Hover) 시 나타날 정보 설정
    fig.update_traces(
        hovertemplate="<b>날짜</b>: %{x|%Y년 %m월 %d일}<br><b>일관객</b>: %{y:,}명<extra></extra>",
        line=dict(width=2.5, color="#E50914"),  # 선 두께 및 색상 설정
        marker=dict(size=6),
    )

    # 레이아웃 미세 조정
    fig.update_layout(
        hovermode="x unified",
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0", tickformat=","),
        margin=dict(l=40, r=40, t=60, b=40),
    )

    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

    # 그래프 해설/인사이트 박스
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** "
        f"'{selected_movie}'의 개봉 초기 관객 집중도, 주말/평일 관객 유입 차이, 그리고 흥행의 지속성을 시간 흐름에 따라 한눈에 파악할 수 있습니다."
    )


# -----------------------------------------------------------------------------
# [구역 2] 추후 새로운 시간 분석 그래프가 추가될 구역 (확장용 레이아웃)
# -----------------------------------------------------------------------------
st.divider()
st.header("📌 Section 2. (추가 예정 구역)")
st.caption(
    "앞으로 이 공간에 기간별 비교, 월별/요일별 패턴 분석 등 시간과 관련된 새로운 그래프가 계속 추가될 예정입니다."
)

# 자리를 비워두거나 플레이스홀더 형태로 구성 가능
with st.container():
    st.text_area(
        label="📝 데이터 메모 / 아이디어 제안",
        value="예: 주말 vs 평일 평균 관객수 비교, 개봉 N주차별 관객 하락율 분석 등",
        height=100,
        disabled=True,
    )
