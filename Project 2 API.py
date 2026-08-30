import sys
import warnings

# Fix pandas "KeyError: warnings"
sys.modules["warnings"] = warnings

import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE Dashboard
st.set_page_config(
    page_title="Brand Visibility Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM CSS

st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #073b70,
        #1263a0,
        #138c88
    );
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

.dashboard-header {
    background: linear-gradient(
        90deg,
        #073b70,
        #1263a0,
        #138c88
    );
    padding: 25px;
    border-radius: 15px;
    color: white;
    margin-bottom: 20px;
}

.dashboard-header h1 {
    margin-bottom: 5px;
}

.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    text-align: center;
    min-height: 130px;
}

.kpi-title {
    font-size: 14px;
    color: #666;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 28px;
    font-weight: bold;
    color: #073b70;
}

.section-title {
    color: #073b70;
    font-size: 24px;
    font-weight: bold;
    margin-top: 15px;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)


# LOAD DATA

df = pd.read_csv(
    r"C:\Users\mchar\brand_visibility_cleaned.csv"
)

# Make a copy for dashboard filtering
data = df.copy()

numeric_columns = [
    "price",
    "rating",
    "reviews",
    "position",
    "brand_visibility_score",
    "review_engagement",
    "review_density"
]

for col in numeric_columns:
    if col in data.columns:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )


# DISCOUNT COLUMN HANDLING

if "discount" not in data.columns:

    # Try to calculate discount from price/raw_price
    if "raw_price" in data.columns:

        raw_price_numeric = pd.to_numeric(
            data["raw_price"],
            errors="coerce"
        )

        if raw_price_numeric.notna().any():

            data["discount"] = (
                (
                    raw_price_numeric - data["price"]
                )
                / raw_price_numeric
                * 100
            )

        else:
            data["discount"] = 0

    else:
        data["discount"] = 0

# BRAND COLUMN

if "brand" not in data.columns:

    data["brand"] = (
        data["title"]
        .astype(str)
        .str.split()
        .str[0]
    )

# SIDEBAR

st.sidebar.markdown(
    """
    <h2>🛒 E-Commerce</h2>
    <p>Brand Visibility Analytics Dashboard</p>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

st.sidebar.markdown("### 🔍 Filters")


# KEYWORD FILTER

if "keyword" in data.columns:

    keyword_options = sorted(
        data["keyword"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_keywords = st.sidebar.multiselect(
        "🔑 KEYWORD",
        keyword_options,
        default=keyword_options
    )

else:

    selected_keywords = []

# BRAND FILTER

if "brand" in data.columns:

    brand_options = sorted(
        data["brand"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_brands = st.sidebar.multiselect(
        "🏷️ BRAND",
        brand_options,
        default=brand_options
    )

else:

    selected_brands = []


# PLATFORM FILTER

if "platform" in data.columns:

    platform_options = sorted(
        data["platform"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_platforms = st.sidebar.multiselect(
        "🏪 PLATFORM",
        platform_options,
        default=platform_options
    )

else:

    selected_platforms = []

# PRICE RANGE

if "price" in data.columns:

    min_price = float(
        data["price"].min()
        if data["price"].notna().any()
        else 0
    )

    max_price = float(
        data["price"].max()
        if data["price"].notna().any()
        else 1000
    )

    if min_price == max_price:
        max_price = min_price + 1

    selected_price = st.sidebar.slider(
        "💰 PRICE RANGE",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price)
    )

else:

    selected_price = (0, 999999)


# RATING RANGE

if "rating" in data.columns:

    selected_rating = st.sidebar.slider(
        "⭐ RATING RANGE",
        min_value=0.0,
        max_value=5.0,
        value=(0.0, 5.0),
        step=0.1
    )

else:

    selected_rating = (0.0, 5.0)


# MAX POSITION

if "position" in data.columns:

    max_position = int(
        data["position"].max()
        if data["position"].notna().any()
        else 40
    )

    if max_position < 1:
        max_position = 40

    selected_position = st.sidebar.slider(
        "📍 MAX POSITION (RANKING)",
        min_value=1,
        max_value=max_position,
        value=max_position
    )

else:

    selected_position = 40


# DATA SOURCE FILTER

source_options = ["All Data"]

if "platform" in data.columns:
    source_options += sorted(
        data["platform"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

selected_source = st.sidebar.selectbox(
    "📁 DATA SOURCE",
    source_options
)


# APPLY FILTERS

filtered_df = data.copy()


if "keyword" in filtered_df.columns and selected_keywords:
    filtered_df = filtered_df[
        filtered_df["keyword"].astype(str).isin(
            selected_keywords
        )
    ]


if "brand" in filtered_df.columns and selected_brands:
    filtered_df = filtered_df[
        filtered_df["brand"].astype(str).isin(
            selected_brands
        )
    ]


if "platform" in filtered_df.columns and selected_platforms:
    filtered_df = filtered_df[
        filtered_df["platform"].astype(str).isin(
            selected_platforms
        )
    ]


if "price" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["price"].between(
            selected_price[0],
            selected_price[1]
        )
    ]


if "rating" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["rating"].between(
            selected_rating[0],
            selected_rating[1]
        )
    ]


if "position" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["position"] <= selected_position
    ]


if selected_source != "All Data" and "platform" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["platform"].astype(str)
        == selected_source
    ]

# HEADER

st.markdown(
    """
    <div class="dashboard-header">

    <h1>📊 Brand Visibility Analytics Dashboard</h1>

    <p>
    E-Commerce Product, Pricing, Platform &
    Ranking Analysis
    </p>

    </div>
    """,
    unsafe_allow_html=True
)


# TABS

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📊 Overview",
        "🏷️ Brand Insights",
        "💰 Pricing Analysis",
        "🏪 Platform Analysis",
        "📈 Visibility & Ranking",
        "🔎 Product Explorer"
    ]
)


# TAB 1 - OVERVIEW

with tab1:

    st.markdown(
        '<div class="section-title">📊 Executive Overview</div>',
        unsafe_allow_html=True
    )

    # KPIs

    total_products = len(filtered_df)

    avg_price = (
        filtered_df["price"].mean()
        if "price" in filtered_df.columns
        else 0
    )

    avg_rating = (
        filtered_df["rating"].mean()
        if "rating" in filtered_df.columns
        else 0
    )

    total_reviews = (
        filtered_df["reviews"].sum()
        if "reviews" in filtered_df.columns
        else 0
    )

    avg_visibility = (
        filtered_df["brand_visibility_score"].mean()
        if "brand_visibility_score"
        in filtered_df.columns
        else 0
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "📦 Total Products",
            f"{total_products:,}"
        )

    with c2:
        st.metric(
            "💰 Avg Price",
            f"${avg_price:,.2f}"
        )

    with c3:
        st.metric(
            "⭐ Avg Rating",
            f"{avg_rating:.2f}"
        )

    with c4:
        st.metric(
            "💬 Total Reviews",
            f"{total_reviews:,.0f}"
        )

    with c5:
        st.metric(
            "👁️ Avg Visibility Score",
            f"{avg_visibility:.2f}"
        )

    st.markdown("---")

    # PRICE DISTRIBUTION

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📊 Price Distribution")

        if "price" in filtered_df.columns:

            fig_price = px.histogram(
                filtered_df,
                x="price",
                nbins=30,
                title="Price Distribution"
            )

            fig_price.update_layout(
                xaxis_title="Price",
                yaxis_title="Number of Products"
            )

            st.plotly_chart(
                fig_price,
                use_container_width=True,
                key="overview_price_distribution"
            )

    # PRODUCTS PER KEYWORD

    with col2:

        st.subheader("🔑 Products per Keyword")

        if "keyword" in filtered_df.columns:

            keyword_count = (
                filtered_df["keyword"]
                .value_counts()
                .reset_index()
            )

            keyword_count.columns = [
                "keyword",
                "count"
            ]

            fig_keyword = px.bar(
                keyword_count,
                x="keyword",
                y="count",
                title="Products per Keyword"
            )

            fig_keyword.update_layout(
                xaxis_title="Keyword",
                yaxis_title="Product Count"
            )

            st.plotly_chart(
                fig_keyword,
                use_container_width=True,
                key="overview_products_keyword"
            )

    # PLATFORM SHARE

    st.subheader("🏪 Platform Share")

    if "platform" in filtered_df.columns:

        platform_count = (
            filtered_df["platform"]
            .value_counts()
            .reset_index()
        )

        platform_count.columns = [
            "platform",
            "count"
        ]

        fig_platform = px.pie(
            platform_count,
            names="platform",
            values="count",
            title="Platform Share"
        )

        st.plotly_chart(
            fig_platform,
            use_container_width=True,
            key="overview_platform_share"
        )

# BRAND INSIGHTS

with tab2:

    st.markdown(
        '<div class="section-title">🏷️ Brand Insights</div>',
        unsafe_allow_html=True
    )

    # TOP BRAND

    if "brand" in filtered_df.columns:

        brand_counts = (
            filtered_df["brand"]
            .value_counts()
        )

        if len(brand_counts) > 0:
            top_brand = brand_counts.index[0]
        else:
            top_brand = "N/A"

    else:

        top_brand = "N/A"

    # AVG VISIBILITY

    if "brand_visibility_score" in filtered_df.columns:

        avg_visibility_brand = (
            filtered_df["brand_visibility_score"]
            .mean()
        )

    else:

        avg_visibility_brand = 0


    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "🏆 Top Brand",
            top_brand
        )

    with c2:
        st.metric(
            "👁️ Avg Visibility Score",
            f"{avg_visibility_brand:.2f}"
        )

    st.markdown("---")

    # BRAND VS PRODUCT COUNT

    if "brand" in filtered_df.columns:

        brand_count = (
            filtered_df["brand"]
            .value_counts()
            .head(15)
            .reset_index()
        )

        brand_count.columns = [
            "brand",
            "product_count"
        ]

        fig_brand_count = px.bar(
            brand_count,
            x="brand",
            y="product_count",
            title="Brand vs Product Count"
        )

        fig_brand_count.update_layout(
            xaxis_title="Brand",
            yaxis_title="Product Count"
        )

        st.plotly_chart(
            fig_brand_count,
            use_container_width=True,
            key="brand_product_count"
        )
    # BRAND VS AVG RATING

    if (
        "brand" in filtered_df.columns
        and "rating" in filtered_df.columns
    ):

        brand_rating = (
            filtered_df
            .groupby("brand")["rating"]
            .mean()
            .sort_values(
                ascending=False
            )
            .head(15)
            .reset_index()
        )

        fig_brand_rating = px.bar(
            brand_rating,
            x="brand",
            y="rating",
            title="Brand vs Average Rating"
        )

        fig_brand_rating.update_layout(
            xaxis_title="Brand",
            yaxis_title="Average Rating"
        )

        st.plotly_chart(
            fig_brand_rating,
            use_container_width=True,
            key="brand_average_rating"
        )

    # TOP BRANDS IN TOP 10 POSITIONS

    if (
        "brand" in filtered_df.columns
        and "position" in filtered_df.columns
    ):

        top10 = filtered_df[
            filtered_df["position"] <= 10
        ]

        top10_brand = (
            top10["brand"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        top10_brand.columns = [
            "brand",
            "top10_count"
        ]

        fig_top10 = px.bar(
            top10_brand,
            x="brand",
            y="top10_count",
            title="Top Brands in Top 10 Positions"
        )

        fig_top10.update_layout(
            xaxis_title="Brand",
            yaxis_title="Products in Top 10"
        )

        st.plotly_chart(
            fig_top10,
            use_container_width=True,
            key="brand_top10"
        )

# PRICING ANALYSIS

with tab3:

    st.markdown(
        '<div class="section-title">💰 Pricing Analysis</div>',
        unsafe_allow_html=True
    )

    # KPIs

    avg_price_pricing = (
        filtered_df["price"].mean()
        if "price" in filtered_df.columns
        else 0
    )

    max_price = (
        filtered_df["price"].max()
        if "price" in filtered_df.columns
        else 0
    )


    # Discounted products
    if "discount" in filtered_df.columns:

        discounted_count = (
            filtered_df["discount"] > 0
        ).sum()

        if len(filtered_df) > 0:

            discount_percentage = (
                discounted_count
                / len(filtered_df)
                * 100
            )

        else:

            discount_percentage = 0

    else:

        discount_percentage = 0


    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "💰 Avg Price",
            f"${avg_price_pricing:,.2f}"
        )

    with c2:
        st.metric(
            "💵 Max Price",
            f"${max_price:,.2f}"
        )

    with c3:
        st.metric(
            "🏷️ % Discounted Products",
            f"{discount_percentage:.2f}%"
        )

    st.markdown("---")

    # PRICE DISTRIBUTION

    if "price" in filtered_df.columns:

        fig_pricing_distribution = px.histogram(
            filtered_df,
            x="price",
            nbins=30,
            title="Price Distribution"
        )

        st.plotly_chart(
            fig_pricing_distribution,
            use_container_width=True,
            key="pricing_distribution"
        )

    # PRICE VS RANKING

    if (
        "price" in filtered_df.columns
        and "position" in filtered_df.columns
    ):

        fig_price_rank = px.scatter(
            filtered_df,
            x="position",
            y="price",
            hover_data=[
                "title"
            ]
            if "title" in filtered_df.columns
            else None,
            title="Price vs Ranking"
        )

        fig_price_rank.update_layout(
            xaxis_title="Ranking Position",
            yaxis_title="Price"
        )

        st.plotly_chart(
            fig_price_rank,
            use_container_width=True,
            key="pricing_vs_ranking"
        )

    # PRICE VS RATING

    if (
        "price" in filtered_df.columns
        and "rating" in filtered_df.columns
    ):

        fig_price_rating = px.scatter(
            filtered_df,
            x="price",
            y="rating",
            title="Price vs Rating"
        )

        fig_price_rating.update_layout(
            xaxis_title="Price",
            yaxis_title="Rating"
        )

        st.plotly_chart(
            fig_price_rating,
            use_container_width=True,
            key="pricing_vs_rating"
        )

#PLATFORM ANALYSIS

with tab4:

    st.markdown(
        '<div class="section-title">🏪 Platform Analysis</div>',
        unsafe_allow_html=True
    )

    # TOTAL PLATFORMS
    if "platform" in filtered_df.columns:

        total_platforms = (
            filtered_df["platform"]
            .nunique()
        )

    else:

        total_platforms = 0

    # BEST PLATFORM

    if (
        "platform" in filtered_df.columns
        and "rating" in filtered_df.columns
    ):

        platform_rating = (
            filtered_df
            .groupby("platform")["rating"]
            .mean()
            .sort_values(
                ascending=False
            )
        )

        if len(platform_rating) > 0:

            best_platform = (
                platform_rating.index[0]
            )

        else:

            best_platform = "N/A"

    else:

        best_platform = "N/A"


    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "🏪 Total Platforms",
            total_platforms
        )

    with c2:

        st.metric(
            "🏆 Best Platform",
            best_platform
        )

    st.markdown("---")

    # PLATFORM VS PRODUCT COUNT

    if "platform" in filtered_df.columns:

        platform_product = (
            filtered_df["platform"]
            .value_counts()
            .reset_index()
        )

        platform_product.columns = [
            "platform",
            "product_count"
        ]

        fig_platform_products = px.bar(
            platform_product,
            x="platform",
            y="product_count",
            title="Platform vs Product Count"
        )

        st.plotly_chart(
            fig_platform_products,
            use_container_width=True,
            key="platform_product_count"
        )

    # PLATFORM VS AVG PRICE

    if (
        "platform" in filtered_df.columns
        and "price" in filtered_df.columns
    ):

        platform_price = (
            filtered_df
            .groupby("platform")["price"]
            .mean()
            .sort_values(
                ascending=False
            )
            .reset_index()
        )

        fig_platform_price = px.bar(
            platform_price,
            x="platform",
            y="price",
            title="Platform vs Average Price"
        )

        st.plotly_chart(
            fig_platform_price,
            use_container_width=True,
            key="platform_average_price"
        )

    # PLATFORM VS AVG RATING

    if (
        "platform" in filtered_df.columns
        and "rating" in filtered_df.columns
    ):

        platform_rating_df = (
            filtered_df
            .groupby("platform")["rating"]
            .mean()
            .sort_values(
                ascending=False
            )
            .reset_index()
        )

        fig_platform_rating = px.bar(
            platform_rating_df,
            x="platform",
            y="rating",
            title="Platform vs Average Rating"
        )

        st.plotly_chart(
            fig_platform_rating,
            use_container_width=True,
            key="platform_average_rating"
        )

#VISIBILITY & RANKING

with tab5:

    st.markdown(
        '<div class="section-title">📈 Visibility & Ranking</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    avg_position = (
        filtered_df["position"].mean()
        if "position" in filtered_df.columns
        else 0
    )

    avg_visibility_score = (
        filtered_df[
            "brand_visibility_score"
        ].mean()
        if "brand_visibility_score"
        in filtered_df.columns
        else 0
    )


    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "📍 Avg Position",
            f"{avg_position:.2f}"
        )

    with c2:

        st.metric(
            "👁️ Avg Visibility Score",
            f"{avg_visibility_score:.2f}"
        )

    st.markdown("---")
    
    # RANKING DISTRIBUTION

    if "position" in filtered_df.columns:

        fig_ranking = px.histogram(
            filtered_df,
            x="position",
            nbins=20,
            title="Ranking Distribution"
        )

        fig_ranking.update_layout(
            xaxis_title="Ranking Position",
            yaxis_title="Number of Products"
        )

        st.plotly_chart(
            fig_ranking,
            use_container_width=True,
            key="ranking_distribution"
        )

    # RATING VS RANKING

    if (
        "rating" in filtered_df.columns
        and "position" in filtered_df.columns
    ):

        fig_rating_rank = px.scatter(
            filtered_df,
            x="position",
            y="rating",
            title="Rating vs Ranking"
        )

        fig_rating_rank.update_layout(
            xaxis_title="Ranking Position",
            yaxis_title="Rating"
        )

        st.plotly_chart(
            fig_rating_rank,
            use_container_width=True,
            key="rating_vs_ranking"
        )

    # REVIEWS VS RANKING

    if (
        "reviews" in filtered_df.columns
        and "position" in filtered_df.columns
    ):

        # Bubble chart
        fig_reviews_rank = px.scatter(
            filtered_df,
            x="position",
            y="reviews",
            size="reviews",
            hover_name="title"
            if "title" in filtered_df.columns
            else None,
            title="Reviews vs Ranking"
        )

        fig_reviews_rank.update_layout(
            xaxis_title="Ranking Position",
            yaxis_title="Reviews"
        )

        st.plotly_chart(
            fig_reviews_rank,
            use_container_width=True,
            key="reviews_vs_ranking"
        )

#PRODUCT EXPLORER

with tab6:

    st.markdown(
        '<div class="section-title">🔎 Product Explorer</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # SEARCH PRODUCT
    # --------------------------------------------------------

    search_text = st.text_input(
        "🔍 Search by product title",
        placeholder="Type product name..."
    )


    explorer_df = filtered_df.copy()


    if search_text:

        if "title" in explorer_df.columns:

            explorer_df = explorer_df[
                explorer_df["title"]
                .astype(str)
                .str.contains(
                    search_text,
                    case=False,
                    na=False
                )
            ]

    # SORT OPTIONS

    sort_options = [
        col
        for col in [
            "title",
            "brand",
            "price",
            "rating",
            "reviews",
            "platform",
            "position",
            "discount"
        ]
        if col in explorer_df.columns
    ]


    if sort_options:

        sort_column = st.selectbox(
            "↕️ Sort by",
            sort_options
        )

        sort_order = st.radio(
            "Sort order",
            [
                "Ascending",
                "Descending"
            ],
            horizontal=True
        )

        explorer_df = explorer_df.sort_values(
            by=sort_column,
            ascending=(
                sort_order == "Ascending"
            )
        )

    # TOP PERFORMING PRODUCTS

    if (
        "position" in explorer_df.columns
        and len(explorer_df) > 0
    ):

        top_products = explorer_df[
            explorer_df["position"] <= 10
        ]

        st.info(
            f"🏆 {len(top_products)} products "
            f"are currently in the Top 10 positions."
        )

    # TABLE COLUMNS

    table_columns = [
        "title",
        "brand",
        "price",
        "rating",
        "reviews",
        "platform",
        "position",
        "discount"
    ]


    available_columns = [
        col
        for col in table_columns
        if col in explorer_df.columns
    ]


    if available_columns:

        st.dataframe(
            explorer_df[
                available_columns
            ],
            use_container_width=True,
            height=600
        )

    else:

        st.warning(
            "No matching columns found."
        )

# FOOTER

st.markdown("---")

st.caption(
    "📊 Brand Visibility Analytics Dashboard | "
    "Built with Python, Pandas, Plotly & Streamlit"
)