def get_sr_by_5_candes(df, ticker, is_line_chart=True, threshold=10, window=5):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # ------------------------
    # Support / Resistance
    # ------------------------
    supports = df[df["Low"] == df["Low"].rolling(window, center=True).min()]["Low"]
    resistances = df[df["High"] == df["High"].rolling(window, center=True).max()]["High"]
    levels_raw = pd.concat([supports, resistances]).sort_index()
    # Keep first level, then only levels far enough from previous one
    levels = levels_raw[abs(levels_raw.diff()) > threshold]
    levels = pd.concat([levels_raw.iloc[[0]], levels]).sort_index()
    print(levels)

    if is_line_chart: 
        plt.figure(figsize=(10, 7))

        df["High"].plot()
        df["Close"].plot()
        df["Low"].plot()

        plt.hlines(
            y=levels.values,
            xmin=levels.index,
            xmax=df.index[-1],
            colors="red"
        )

        plt.xlabel("Date", fontsize=14, fontweight="bold")
        plt.ylabel("Price")
        plt.title(f"{ticker} Support and Resistance Levels")
        plt.grid(True)
        plt.show()

    # ------------------------
    # Candlestick Plot
    # ------------------------
    fig, axes = mpf.plot(
        df,
        type='candle',
        style='charles',
        figsize=(14, 8),
        volume=False,
        returnfig=True,
        title=f'{ticker} Support & Resistance'
    )

    ax = axes[0]

    # Draw S/R lines from detection date to last candle
    for dt, level in levels.items():

        start_idx = df.index.get_loc(dt)
        end_idx = len(df.index) - 1

        ax.hlines(
            y=level,
            xmin=start_idx,
            xmax=end_idx,
            colors='red',
            linewidth=2
        )

    plt.show()