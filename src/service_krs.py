import re
import pandas as pd

ALLOWED_TECH_DATES = {
    "1900-01-01",
    "1970-01-01",
    "2100-01-01",
    "5999-12-31",
    "9999-12-31",
}

CRITICAL_COLS_BY_TABLE: dict[str, set[str]] = {
    "ads_tis_deriv_secur_positions_deriv_sp": {
        "rec_num",
        "ucr_subject_id",
        "isin",
        "dealdate",
        "rep_date",
        "amount",
        "dealcurr",
        "buysell",
        "odsprocessed_dt",
        "odseffective_from_dt",
    },
        "ads_tis_securities_portfolio_securities_prf": {
        "rec_num",
        "ucr_subject_id",
        "isin",
        "report_date",
        "issuer",
        "volume",
        "amount",
        "currency",
        "odsprocessed_dt",
        "odseffective_from_dt",
    },
    "cbonds_emission_ratings": {
        "id",
        "emission_id",
        "date",
        "operdate",
        "row_hash",
    },
    "cbonds_emitent_ratings": {
        "id",
        "emitent_id",
        "date",
        "operdate",
        "row_hash",
    },
    "cbonds_trading_grounds": {
        "id",
        "name_eng",
        "country",
        "operdate",
        "row_hash",
    },
    "cbonds_tradings": {
        "id",
        "emission_id",
        "trading_ground_id",
        "date",
        "operdate",
        "row_hash",
    },
    "ukvoodm_fxir_trades_cf": {
        "id",
        "dealnumber",
        "paymentdate",
        "cashflowamount",
        "paymentcurrency",
        "reportdate",
        "odsprocessed_dt",
        "odseffective_from_dt",
    },
    "ukvoodm_fxir_trades_std": {
        "id",
        "dealnumber",
        "dealtype",
        "clientcode",
        "clientname",
        "reportdate",
        "odsprocessed_dt",
        "odseffective_from_dt",
    },
    "olb_rtscontract": {
        "key",
        "instr_short",
        "isin",
        "class",
        "mat_date",
        "last_trade_date",
        "operdate",
        "actualdate",
        "cur",
        "lot",
        "step_price",
        "go_buy",
        "go_sell",
    },
    "olb_rtsposition": {
        "account",
        "instr_short",
        "key",
        "curr",
        "mat_date",
        "operdate",
        "actualdate",
        "open_net",
        "cur_net",
        "plan_net_pos_est",
        "var_marg",
        "price",
        "eff_price",
        "lk1",
        "lk2",
    },
}

STRING_CODE_COLS = {
    "isin",
    "emission_isin_code",
    "isin_code",
    "isin_code_144a",
    "isin_code_3",
    "inn",
    "emitent_inn",
    "emitent_inn_ua",
    "account",
    "cashflowaccount",
    "acc52601",
    "acc52602",
    "acc_52601",
    "acc_52602",
    "demandaccnum",
    "obligaccnum",
    "collatdepositacc",
    "collateralacc",
    "dealnumber",
    "clientcode",
    "contragentcode",
    "key",
    "row_hash",
    "mic",
    "operating_mic",
    "instr_short",
    "agreement_number",
    "national_regnumber",
    "national_reg_number",
    "state_registration_number",
}

ACCOUNT_COLS = {
    "account",
    "cashflowaccount",
    "acc52601",
    "acc52602",
    "acc_52601",
    "acc_52602",
    "demandaccnum",
    "obligaccnum",
    "collatdepositacc",
    "collateralacc",
}

CURRENCY_COLS = {
    "dealcurr",
    "dealcurr_rasch",
    "dealcurr_nom",
    "bonuscurr",
    "stock_cur",
    "tss_ccy",
    "margin_currency",
    "paymentcurrency",
    "buycurrency",
    "sellcurrency",
    "cur",
    "curr",
    "nominal_currency",
    "price_currency",
    "nominalcb_ccy",
    "market_cost_cur",
    "market_price_straik_ccy",
    "deltacalypsocurr",
    "deltacurrency",
    "demandovpcurr",
    "obligovpcurr",
    "termnettingcurr1",
    "termnettingcurr2",
    "termnettingcurr3",
}

NUMERIC_OVERRIDE_COLS = {
    "cost_in_bookdate",
    "cost_in_bookdate_rub",
    "acc52602balance",
    "acc52601balance",
    "value_krs_delta_rub",
    "nominalrub",
    "marketvaluerub",
    "cashflowamount",
    "buyamount",
    "sellamount",
    "amount",
    "volume",
    "marketvalue",
    "nominal_value",
    "currency",  # в cbonds_trading_grounds там числовой ID валюты (1, 31, 41)
}
EXPECTED_COLUMNS_BY_TABLE: dict[str, list[str]] = {
    "ads_tis_deriv_secur_positions_deriv_sp": [
        "ost_52602", "value_krs_delta_rub", "is_pfi", "deal_wcka", "srokrealizaciizaloga",
        "folder_kondor_id", "activeshortname", "currencyofgeneralsoglashenie",
        "value_of_volatility", "amount_claim_cur_ovp_ccy", "acc_52601", "dealcurr_rasch",
        "bloomberg_code", "value_delta_rub", "cost_bond", "coefficient_gamma",
        "odsprocessed_dt", "emit_raiting", "konec_zaem", "value_krs_delta_pct",
        "firstdate", "coupon_near_date", "kurs_date", "amount_claim_rur",
        "optionacc526_ost", "amount_liab_cur_ovp_ccy", "companyname", "acc_liability",
        "pricedif", "cost_in_bookdate", "isin", "odseffective_to_csn", "optiontype",
        "date_decision", "activetypename", "optionexecticket", "market_cost_cur",
        "acc_52602", "odsupdate_id", "dealcurr_nom", "nameofindex", "buysell",
        "acc_firstdate_debet", "market_price_straik", "ucr_subject_id", "rec_num",
        "odsdeleted_flg", "folder_kondor", "bonuscurr", "acc_claim", "optionstyle",
        "stock_cur", "coefficient_vega", "nominaldeal", "is_pct", "dealprice",
        "amount_liability_rur", "cn_contracts_id", "paymentperiod_valdat2", "market_cost",
        "amount_claim_cur_ovp", "nkd", "odseffective_from_csn", "dealtype", "isnewdeal",
        "odseffective_from_dt", "amount_liability_cur_ovp", "trade_area_name",
        "bonusamount", "couponrate", "maturitydate", "nominalcb_ccy",
        "cost_bal_without_nkd", "compens_agreement_num", "deal_id_kondor", "cb_raiting",
        "likvidac_netting", "cn_contracts_bd", "tss_rur", "dateofreginrepositarii",
        "contragentcode", "dogovorvrepositarii", "value_delta_pct", "amount",
        "dealtypewithoption", "nominalcb_summ", "pereoc_period", "tss_ccy", "dealdate",
        "amount_claim_cur", "ticket", "contragent", "amount_liability_cur_ccy",
        "marketvalue", "acc_firstdate_credit", "tss_val", "optionexecfactdate",
        "margin_sum", "national_regnumber", "odseffective_to_dt",
        "state_registration_number", "market_price_straik_ccy", "paymentperiod_valdat1",
        "odsis_active_flg", "amount_claim_cur_ccy", "ost_52601", "coefficient_delta",
        "coefficient_delta_calypso", "lastmodifdate", "odscreate_id",
        "floating_rate_type", "ins_date", "margin_currency", "optionaccount526",
        "amount_liability_cur", "margin_period", "bonusdate", "dealcurr",
        "deal_id_calypso", "bookdate", "dealtypebirg", "generalsoglashenie",
        "rep_date", "cost_stock", "hdp_processed_dttm",
        "partition_month_odseffective_from_dt", "partition_month_odseffective_to_dt",
    ],
    "ads_tis_securities_portfolio_securities_prf": [
        "inn", "type_coup_rate", "odsprocessed_dt", "volume_pzt_overvalue", "account",
        "plan_early_repayment_date", "isin", "odseffective_to_csn", "over_vol_71",
        "adjustment_incr", "odsupdate_id", "volume_prem", "ucr_subject_id", "rec_num",
        "odsdeleted_flg", "volume_pkd", "currency", "create_date", "adjustment_redu",
        "volume_ngt_overvalue", "offer_type", "over_vol_70", "odseffective_from_csn",
        "result_not_fix", "odseffective_from_dt", "sectypename", "volume_discont",
        "volume", "maturity_date", "amount", "secinterest", "adjustment_acc",
        "coup_near_date", "odseffective_to_dt", "national_reg_number", "odsis_active_flg",
        "issuer", "ogress_issuer_id", "nominal_value", "volume_nkd", "odscreate_id",
        "report_date", "result", "hdp_processed_dttm",
        "partition_month_odseffective_from_dt", "partition_month_odseffective_to_dt",
    ],
    "cbonds_emission_ratings": [
        "id", "agency_id", "agency_name_eng", "agency_name_rus", "date",
        "emitent_branch_id", "emission_emitent_country_id",
        "emission_emitent_country_region_id", "emission_emitent_id",
        "emission_emitent_name_eng", "emission_emitent_name_rus", "emission_id",
        "emission_isin_code", "emission_number_eng", "emission_number_rus",
        "emission_state_reg_number", "forecast_id", "forecast_name_eng",
        "forecast_name_rus", "scale_id", "scale_name_eng", "scale_name_rus",
        "scale_point_id", "scale_point_name", "updating_date", "row_hash",
        "operdate", "show_ru",
    ],
    "cbonds_emitent_ratings": [
        "id", "agency_id", "agency_name_eng", "agency_name_rus", "date",
        "emission_emitent_name_eng", "emission_emitent_name_rus", "emitent_country_id",
        "emitent_country_region_id", "emitent_id", "emitent_inn", "emitent_inn_ua",
        "emitent_lei", "forecast_id", "forecast_name_eng", "forecast_name_rus",
        "scale_id", "scale_name_eng", "scale_name_rus", "scale_point_id",
        "scale_point_name", "updating_date", "row_hash", "operdate",
        "emitent_branch_id", "emission_emitent_country_id",
        "emission_emitent_country_region_id", "emission_emitent_id", "emission_id",
        "emission_isin_code", "emission_number_eng", "emission_number_rus",
        "emission_state_reg_number", "show_ru", "src_update_time", "created_at",
    ],
    "cbonds_trading_grounds": [
        "country", "country_name_eng", "country_name_rus", "currency",
        "full_name_eng", "full_name_rus", "id", "info_eng", "info_rus",
        "name_eng", "name_rus", "operating_mic", "region", "subregion",
        "web_site_url", "row_hash", "operdate", "acronym",
        "trading_grounds_kinds_id", "mic", "trading_sessions_kinds_id",
    ],
    "cbonds_tradings": [
        "id", "admittedquote", "agreement_number", "avar_price", "board_id",
        "buying_quote", "clearance_profit", "clearance_profit_effect",
        "clearance_profit_nominal", "convexity", "convexity_offer", "date",
        "dur", "dur_mod", "dur_mod_to", "dur_to", "emission_emitent_country_id",
        "emission_emitent_country_region_id", "emission_emitent_id", "emission_id",
        "indicative_price", "indicative_price_type", "indicative_yield",
        "indicative_yield_type", "last_price", "legalcloseprice", "marketprice",
        "marketprice2", "max_price", "mid_price", "min_price", "nkd",
        "offer_date", "offer_profit", "offer_profit_effect", "offer_profit_nominal",
        "open_price", "overturn", "pvbp", "pvbp_offer", "selling_quote",
        "trading_ground_id", "volume", "volume_money", "years_to_maturity",
        "ytm_bid", "ytm_close", "ytm_last", "ytm_max", "ytm_min", "ytm_offer",
        "ytm_open", "yto_bid", "yto_close", "yto_last", "yto_offer",
        "bid_ask_spread", "g_spread", "t_spread", "t_spread_benchmark",
        "isin_code", "isin_code_144a", "isin_code_3", "document_eng",
        "document_rus", "document_pol", "document_ita", "emission_kind_id",
        "coupon_profit_effect", "ytc_bid", "ytc_offer", "ytc_last", "ytc_close",
        "row_hash", "operdate", "created_at", "updated_at",
    ],
    "ukvoodm_fxir_trades_cf": [
        "odseffective_from_dt", "odseffective_to_dt", "odseffective_from_csn",
        "odseffective_to_csn", "odsis_active_flg", "odsdeleted_flg", "odscreate_id",
        "odsupdate_id", "odsprocessed_dt", "id", "dealnumber", "cashflowaccount",
        "swapleg", "startdate", "enddate", "cashflowtype", "paymentdate",
        "cashflowamount", "paymentcurrency", "reportdate", "hdp_processed_dttm",
    ],
    "ukvoodm_fxir_trades_std": [
        "odseffective_from_dt", "odseffective_to_dt", "odseffective_from_csn",
        "odseffective_to_csn", "odsis_active_flg", "odsdeleted_flg", "odscreate_id",
        "odsupdate_id", "odsprocessed_dt", "id", "reportdate", "dealtype",
        "dealnumber", "clientcode", "clientname", "demandaccnum", "demandsumrub",
        "obligaccnum", "obligsumrub", "isexchange", "isbuy", "compensagreement",
        "nominalrub", "marketvaluerub", "valuedate", "balancestartdate", "buyamount",
        "buycurrency", "sellamount", "sellcurrency", "note", "rating",
        "isderivative", "acc52601", "acc52601balance", "acc52602", "acc52602balance",
        "collateraldeposit", "collatdepositacc", "collateraltype", "collateralacc",
        "collatsumrub", "demandcurrcode", "obligcurrcode", "maturitydate",
        "rcvlegrateisfixed", "rcvlegfixrate", "rcvlegfloatrate",
        "rcvlegfloatratetenor", "rcvnearrateresetdate", "paylegrateisfixed",
        "paylegfixrate", "paylegfloatrate", "paylegfloatratetenor",
        "paynearrateresetdate", "demanddepositsumrub", "obligdepositsumrub",
        "optionpremium", "masteragreement", "masteragrtype", "masteragrdate",
        "terminatednetting", "termnettingcurr1", "termnettingcurr2",
        "termnettingcurr3", "repositaryregdate", "repositaryregnumber", "dailyreval",
        "centralcpty", "demandsumovp", "obligsumovp", "solutiondate", "iscall",
        "deltaold", "delta", "gamma", "vega", "volatility", "deltacalypsocurr",
        "deltacurrency", "kondorid", "fixingdate", "paymentcurrency",
        "demandpaymentsum", "obligpaymentsum", "strike", "demandovprub",
        "demandovpcurr", "obligovprub", "obligovpcurr", "deltarub",
        "kondorfoldername", "calypsoid", "code_mdm", "rrdeltarub", "rrdeltapct",
        "krsdeltarub", "krsdeltapct", "demandsumval", "obligsumval",
        "hdp_processed_dttm", "partition_month_odseffective_from_dt",
        "partition_month_odseffective_to_dt",
    ],
    "olb_rtscontract": [
        "descrip", "descrip_ext", "base_a_group", "contractgroupname", "base_asset",
        "extb_price", "anon_trade", "go_buy", "go_sell", "bgop", "bgonp", "cur",
        "vol", "mat_date_beg", "mat_date", "last_trade_date", "trda_date",
        "till_mat_days", "instr_short", "isin", "class", "clearing_quote", "lot",
        "prod_type", "option_type", "session_state", "status", "status_kl", "strike",
        "securityclassdescription", "price_type", "price_min_step", "step_price",
        "last_p_2", "close_p", "code_extb", "actualdate", "key", "operdate",
        "partition_actualdate",
    ],
    "olb_rtsposition": [
    "account", "instr_short", "mat_date", "open_net", "cur_net",
    "plan_net_pos_est", "var_marg", "eff_price", "price", "curr",
    "market_risk", "market_risk1", "market_risk2", "lk1", "lk2",
    "actualdate", "key", "operdate", "partition_actualdate",
    ],
}
def _detect_source_id(table_name: str) -> int:
    name = table_name.lower()
    if name.startswith("ads_tis"):
        return 1
    if name.startswith("cbonds"):
        return 2
    if name.startswith("ukvoodm"):
        return 3
    if name.startswith("olb"):
        return 4
    return 0


def _resolve_schema_key(table_name: str) -> str | None:
    name = table_name.lower().strip()
    return next(
        (k for k in EXPECTED_COLUMNS_BY_TABLE if name.startswith(k) or k in name),
        None,
    )


def _fix_unparsed_dollar_df(df: pd.DataFrame) -> pd.DataFrame:
    na_markers = ["", "None", "none", "NONE", "NULL", "null", "NaN", "nan", "N/A", "n/a", '""']
    if len(df.columns) == 1 and "$" in str(df.columns[0]):
        header = [h.strip() for h in str(df.columns[0]).split("$")]
        col_name = df.columns[0]
        split_rows = df[col_name].fillna("").astype(str).apply(lambda s: s.split("$"))
        fixed_data = [
            row[: len(header)] + [""] * max(0, len(header) - len(row))
            for row in split_rows
        ]
        fixed_df = pd.DataFrame(fixed_data, columns=header, index=df.index)
        return fixed_df.replace(na_markers, pd.NA)
    return df.replace(na_markers, pd.NA)


def _infer_col_kind(col_name: str, source_id: int) -> str:
    c = col_name.lower().strip()
    if c in NUMERIC_OVERRIDE_COLS:
        return "numeric"
    if c in ACCOUNT_COLS:
        return "account"
    if (
        c in CURRENCY_COLS
        or c.endswith("_curr")
        or c.endswith("_currency")
        or c.endswith("_ccy")
        or c.endswith("currcode")
    ):
        return "currency"
    if c == "isin" and source_id == 1:
        return "isin"
    if c in STRING_CODE_COLS:
        return "string_code"
    if (
        c == "date"
        or c.endswith("_date")
        or c.endswith("date")
        or c.endswith("_dt")
        or c.endswith("_dttm")
    ):
        return "date"
    if c.endswith("_type") or c.endswith("_name"):
        return "text"
    if any(
        c == k or c.endswith(f"_{k}") or c.startswith(f"{k}_")
        for k in (
            "id", "num", "amount", "volume", "price", "rate", "balance",
            "sum", "rub", "usd", "delta", "gamma", "vega", "theta", "rho",
            "strike", "lot", "go", "lk1", "lk2", "ytm", "yto", "ytc", "nkd",
        )
    ):
        return "numeric"
    return "text"


def _is_critical_col(col_name: str, schema_key: str | None) -> bool:
    if schema_key is None:
        return False
    return col_name.lower().strip() in CRITICAL_COLS_BY_TABLE.get(schema_key, set())
_DATE_RE = re.compile(
    r"^(?:\d{4}-\d{2}-\d{2}(?:[T\s]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?"
    r"|\d{2}\.\d{2}\.\d{4}(?:\s\d{2}:\d{2}(?::\d{2})?)?"
    r"|\d{8})$"
)
_NUMERIC_RE = re.compile(r"^[+-]?(?:\d+(?:[.,]\d+)?|[.,]\d+)(?:[eE][+-]?\d+)?$")
_CURRENCY_RE = re.compile(r"^(?:[A-Z]{3}|\d{3})$")
_ISIN_RE = re.compile(r"^[A-Z]{2}[A-Z0-9]{10}$")
_DIGITS_ONLY_RE = re.compile(r"^\d+$")
_OLB_ACC_RE = re.compile(r"^[A-Za-z0-9*]+$")
_EMPTY_TOKENS = {"", "None", "none", "NONE", "NULL", "null", "NaN", "nan", '""', "''"}


def _empty_mask(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype(str).str.strip().isin(_EMPTY_TOKENS)

_NAMED_ENTITY_COLS = {
    "issuer",
    "clientname",
    "contragent",
    "companyname",
    "name_eng",
    "name_rus",
    "full_name_eng",
    "full_name_rus",
    "emission_name_eng",
    "emission_name_rus",
    "emission_emitent_name_eng",
    "emission_emitent_name_rus",
    "scale_name_eng",
    "scale_name_rus",
    "scale_point_name",
    "securityclassdescription",
    "contractgroupname",
    "descrip",
    "descrip_ext",
    "comment",
    "note",
    "info_eng",
    "info_rus",
    "web_site_url",
    "website",
    "acronym",
}


NON_NEGATIVE_COLS = {
    "id",
    "rec_num",
    "ucr_subject_id",
    "lot",
    "volume",
    "volume_money",
    "admittedvolume",
    "deals_count",
    "num_trades",
    "nominal_value",
    "nominaldeal",
    "nominalcb_summ",
    "facevalue",
    "cost_in_bookdate",
    "cost_in_bookdate_rub",
    "cost_bond",
    "cost_stock",
    "cost_bal_without_nkd",
    "marketvalue",
    "market_cost",
    "price",
    "eff_price",
    "last_price",
    "open_price",
    "min_price",
    "max_price",
    "mid_price",
    "bid",
    "ask",
    "buying_quote",
    "selling_quote",
    "admittedquote",
    "avar_price",
    "legalcloseprice",
    "marketprice",
    "marketprice2",
    "marketprice3",
    "ind_price",
    "indicative_price",
    "dealprice",
    "strike",
    "market_price_straik",
    "go_buy",
    "go_sell",
    "bgop",
    "bgonp",
    "couponrate",
    "nkd",
    "volume_nkd",
    "dur",
    "duration",
    "dur_mod",
    "duration_modified",
    "dur_to",
    "dur_mod_to",
    "till_mat_days",
    "years_to_maturity",
    "volatility",
    "value_of_volatility",
    "gamma",
    "vega",
    "convexity",
    "convexity_offer",
    "pvbp",
    "pvbp_offer",
}


def _invalid_series_mask(series: pd.Series, col_kind: str, source_id: int, empty: pd.Series) -> pd.Series:
    non_empty = ~empty
    total_non_empty = int(non_empty.sum())
    if total_non_empty == 0:
        return pd.Series(False, index=series.index)

    s = series.fillna("").astype(str).str.strip()
    col_lower = str(series.name or "").lower().strip()

    if col_kind in {"text", "string_code"}:
        if total_non_empty >= 3:
            sub = s[non_empty]
            cleaned = sub.str.replace(" ", "", regex=False).str.replace("\xa0", "", regex=False)
            num_mask = cleaned.str.match(_NUMERIC_RE)
            if num_mask.mean() >= 0.95 and not num_mask.all():
                bad = pd.Series(False, index=series.index)
                bad.loc[sub.index] = ~num_mask
                return bad

            is_named_or_url = col_lower in _NAMED_ENTITY_COLS or col_lower.endswith("_url")
            if col_kind == "text" and total_non_empty >= 5 and not is_named_or_url:
                no_digits_mask = ~sub.str.contains(r"\d", regex=True)
                if no_digits_mask.mean() >= 0.95 and not no_digits_mask.all():
                    bad = pd.Series(False, index=series.index)
                    bad.loc[sub.index] = ~no_digits_mask
                    return bad
        return pd.Series(False, index=series.index)

    if col_kind == "numeric":
        cleaned = s.str.replace(" ", "", regex=False).str.replace("\xa0", "", regex=False)
        bad_fmt = non_empty & ~cleaned.str.match(_NUMERIC_RE)

        if col_lower in NON_NEGATIVE_COLS or col_lower.endswith("_id"):
            valid_num_mask = non_empty & ~bad_fmt
            if valid_num_mask.any():
                nums = pd.to_numeric(
                    cleaned[valid_num_mask].str.replace(",", ".", regex=False),
                    errors="coerce",
                )
                bad_sign = nums.le(0) if col_lower == "lot" else nums.lt(0)
                bad_fmt.loc[nums.index] |= bad_sign.fillna(False)

        return bad_fmt

    if col_kind == "currency":
        return non_empty & ~s.str.match(_CURRENCY_RE)

    if col_kind == "isin":
        return non_empty & ~s.str.match(_ISIN_RE)

    if col_kind == "account":
        s_acc = s.str.replace(r"\.0$", "", regex=True)
        has_exp = s_acc.str.lower().str.contains("e+", regex=False) | s_acc.str.lower().str.contains("e-", regex=False)
        pattern = _OLB_ACC_RE if source_id == 4 else _DIGITS_ONLY_RE
        return non_empty & (has_exp | ~s_acc.str.match(pattern))

    if col_kind == "date":
        bad = pd.Series(False, index=series.index)
        sub = s[non_empty]
        tech = sub.str.slice(0, 10).isin(ALLOWED_TECH_DATES)
        check_sub = sub[~tech]
        if check_sub.empty:
            return bad

        fmt_ok = check_sub.str.match(_DATE_RE)
        bad.loc[check_sub.index] = ~fmt_ok

        valid_fmt = check_sub[fmt_ok]
        if not valid_fmt.empty:
            is_8 = valid_fmt.str.len() == 8
            is_dot = valid_fmt.str.slice(0, 6).str.contains(".", regex=False)
            if is_8.any():
                parsed_8 = pd.to_datetime(valid_fmt[is_8], format="%Y%m%d", errors="coerce")
                bad.loc[valid_fmt[is_8].index] = parsed_8.isna()
            if is_dot.any():
                parsed_dot = pd.to_datetime(valid_fmt[is_dot], dayfirst=True, errors="coerce")
                bad.loc[valid_fmt[is_dot].index] = parsed_dot.isna()
            iso = valid_fmt[~is_8 & ~is_dot]
            if not iso.empty:
                parsed_iso = pd.to_datetime(iso, errors="coerce")
                bad.loc[iso.index] = parsed_iso.isna()
        return bad

    return pd.Series(False, index=series.index)



def _check_table_schema(
    schema_key: str | None,
    columns: list[str],
) -> tuple[list[str], list[str]]:
    broken = [
        str(c) for c in columns
        if str(c).strip() == "" or str(c).startswith("Unnamed:") or re.search(r"\.\d+$", str(c))
    ]
    if broken:
        return [f"поврежден/отсутствует заголовок ({', '.join(broken)})"], []

    if schema_key is None:
        return [], []

    expected_cols = EXPECTED_COLUMNS_BY_TABLE[schema_key]
    expected_set = set(expected_cols)

    clean_actual = [str(c).strip() for c in columns]
    actual_lower_set = {c.lower() for c in clean_actual}

    missing = [c for c in expected_cols if c not in actual_lower_set]
    extra = [c for c in clean_actual if c.lower() not in expected_set]

    missing_critical = [c for c in missing if _is_critical_col(c, schema_key)]
    missing_regular = [c for c in missing if c not in missing_critical]

    warnings: list[str] = []
    if missing_regular:
        warnings.append(f"отсутствуют обычные столбцы ({', '.join(missing_regular)})")
    if extra:
        warnings.append(f"обнаружены лишние столбцы ({', '.join(extra)})")

    return missing_critical, warnings


def _validate_table(table_name: str, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    source_id = _detect_source_id(table_name)
    schema_key = _resolve_schema_key(table_name)

    if "__load_error__" in df.columns:
        err = str(df["__load_error__"].iloc)
        return pd.DataFrame(), {
            "source_id": source_id,
            "total_rows": 0,
            "removed_rows": 0,
            "row_errors": [f"ошибка чтения файла: {err}"],
            "schema_warnings": [],
        }

    work_df = _fix_unparsed_dollar_df(df.copy())
    total_rows = len(work_df)

    missing_critical, schema_warnings = _check_table_schema(
        schema_key, list(work_df.columns)
    )
    if missing_critical:
        reason = f"схема: отсутствует критический столбец ({', '.join(missing_critical)})"
        return pd.DataFrame(columns=work_df.columns), {
            "source_id": source_id,
            "total_rows": total_rows,
            "removed_rows": total_rows,
            "row_errors": [reason],
            "schema_warnings": schema_warnings,
        }

    broken_headers = [
        c for c in work_df.columns
        if str(c).startswith("Unnamed:") or re.search(r"\.\d+$", str(c))
    ]
    if broken_headers:
        work_df = work_df.drop(columns=broken_headers)

    # Векторный поиск 100% пустых столбцов
    empty_masks = {c: _empty_mask(work_df[c]) for c in work_df.columns}
    empty_cols = [c for c, mask in empty_masks.items() if mask.all()]
    if empty_cols:
        work_df = work_df.drop(columns=empty_cols)

    # Векторная проверка по колонкам вместо построчного iterrows
    error_reasons_by_idx: dict[int, list[str]] = {}
    any_invalid = pd.Series(False, index=work_df.index)

    for col in work_df.columns:
        s = work_df[col]
        empty = empty_masks[col]
        kind = _infer_col_kind(str(col), source_id)
        is_crit = _is_critical_col(str(col), schema_key)

        if is_crit and empty.any():
            any_invalid |= empty
            for pos in work_df.index[empty]:
                error_reasons_by_idx.setdefault(int(pos), []).append(
                    f"пропуск в критическом поле '{col}'"
                )

        bad_fmt = _invalid_series_mask(s, kind, source_id, empty)
        if bad_fmt.any():
            any_invalid |= bad_fmt
            for pos in work_df.index[bad_fmt]:
                val_str = str(s.loc[pos]).strip()
                error_reasons_by_idx.setdefault(int(pos), []).append(
                    f"{col}: некорректное значение ({val_str})"
                )

    # Бизнес-правило для olb_rtscontract: option_type обязателен для Опционов
    col_map_lower = {c.lower(): c for c in work_df.columns}
    if source_id == 4 and "option_type" in col_map_lower and "class" in col_map_lower:
        cls_col = col_map_lower["class"]
        opt_col = col_map_lower["option_type"]
        is_opt = work_df[cls_col].fillna("").astype(str).str.lower().str.contains("опцион", regex=False)
        opt_missing = is_opt & empty_masks[opt_col]
        if opt_missing.any():
            any_invalid |= opt_missing
            for pos in work_df.index[opt_missing]:
                error_reasons_by_idx.setdefault(int(pos), []).append(
                    "пропуск 'option_type' для контракта класса Опцион"
                )

    row_errors = [
        f"стр. {pos + 2}: {'; '.join(error_reasons_by_idx[pos])}"
        for pos in sorted(error_reasons_by_idx)
    ]
    clean_df = work_df[~any_invalid].copy()
    removed_rows = total_rows - len(clean_df)

    return clean_df, {
        "source_id": source_id,
        "total_rows": total_rows,
        "removed_rows": removed_rows,
        "row_errors": row_errors,
        "schema_warnings": schema_warnings,
    }


def process_krs_load(
    process_id: str,
    tables: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, list[str]]:
    logs: list[str] = [f"[{process_id}] Запуск валидации данных модуля krs_load"]

    if not tables:
        logs.append(f"[{process_id}] Входные таблицы не найдены.")
        return pd.DataFrame(columns=["Метрика", "Сумма (RUB)"]), logs

    source_titles = {
        1: "Источник 1 (Портфели ads_tis_*)",
        2: "Источник 2 (Рейтинги и торги cbonds_*)",
        3: "Источник 3 (Сделки ukvoodm_*)",
        4: "Источник 4 (Брокерский бизнес olb_*)",
        0: "Прочие таблицы",
    }
    stats_by_source = {
        sid: {"tables": 0, "total": 0, "removed": 0, "details": []}
        for sid in source_titles
    }

    for tbl_name, tbl_df in sorted(tables.items()):
        _, info = _validate_table(tbl_name, tbl_df)
        sid = info["source_id"]
        stats_by_source[sid]["tables"] += 1
        stats_by_source[sid]["total"] += info["total_rows"]
        stats_by_source[sid]["removed"] += info["removed_rows"]

        for warn in info.get("schema_warnings", []):
            stats_by_source[sid]["details"].append(f"  [Схема] {tbl_name}: {warn}")

        if info["row_errors"]:
            stats_by_source[sid]["details"].append(
                f"  Таблица '{tbl_name}' (удалено {info['removed_rows']} из {info['total_rows']}):"
            )
            for err_line in info["row_errors"][:30]:
                stats_by_source[sid]["details"].append(f"    {err_line}")
            if len(info["row_errors"]) > 30:
                rest = len(info["row_errors"]) - 30
                stats_by_source[sid]["details"].append(f"    ... и еще {rest} ошибок")

    total_all = 0
    removed_all = 0
    for sid in (1, 2, 3, 4, 0):
        st = stats_by_source[sid]
        if st["tables"] == 0:
            continue
        total_all += st["total"]
        removed_all += st["removed"]
        logs.append(
            f"{source_titles[sid]}: таблиц={st['tables']}, всего строк={st['total']}, "
            f"удалено={st['removed']}, валидных={st['total'] - st['removed']}"
        )
        logs.extend(st["details"])

    valid_all = total_all - removed_all
    logs.append(
        f"[{process_id}] Итого по krs_load: всего={total_all}, валидных={valid_all}, удалено={removed_all}"
    )

    summary_df = pd.DataFrame(
        [
            {"Метрика": "krs_load: Всего проверено строк", "Сумма (RUB)": float(total_all)},
            {"Метрика": "krs_load: Валидных строк", "Сумма (RUB)": float(valid_all)},
            {"Метрика": "krs_load: Отбраковано строк", "Сумма (RUB)": float(removed_all)},
        ]
    )

    return summary_df, logs
