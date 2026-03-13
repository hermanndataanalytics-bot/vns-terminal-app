# ==========================================
                # 6. GEMINI CIO BRIEFING
                # ==========================================
                st.markdown("---")
                st.subheader("🧠 Institutional AI Intelligence")

                if st.button(
                    "🤖 GENERATE CIO BRIEFING",
                    use_container_width=True,
                    key="btn_cio_gemini"
                ):

                    client = get_ai_client()

                    if client is None:
                        st.error("AI system unavailable. API key missing.")
                    else:

                        with st.spinner("Gemini Flash is analyzing market structure..."):

                            prompt = f"""
                Act as a Chief Investment Officer (CIO) of a hedge fund.

                Analyze this Forex / Gold trade:

                Asset: {ticker_name}
                Current Price: {current_price}
                ATR Volatility: {atr:.5f}
                Risk per Trade: {risk_pct_input*100:.2f}%
                Recommended Lot Size: {st.session_state.get("calculated_lot",0)}
                Stop Loss: {sl_pips:.1f} pips
                Take Profit: {tp_pips:.1f} pips (Risk Reward 1:2)

                Provide a concise institutional briefing (maximum 3 sentences).

                Focus on:
                • Risk quality
                • Whether ATR supports the stop loss
                • Institutional trade viability

                End the response with:
                [SCORE: XX]
                Where XX is a confidence score between 0 and 100.
                """

                            try:

                                res = client.models.generate_content(
                                    model="gemini-2.5-flash",
                                    contents=prompt
                                )

                                full_text = res.text

                     
