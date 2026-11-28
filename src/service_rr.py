"""
service_rr.py — валидация данных для модуля rr_calc (рыночный риск).
"""
import re
from typing import Dict, List, Optional, Set, Tuple, Any
import pandas as pd

# 1. Конфигурация

SOURCE_PATTERNS = [
    ("f0409634", 1),
    ("allcurvesquotes", 2),
    ("securities_positions", 2),
    ("cbonds_emissions", 3),
    ("cbonds_stocks", 3),
    ("livetrades", 4),
    ("mortage_amortization", 4),
    ("mortgage_amortization", 4),
]

SOURCE_TITLES = {
    1: "Источник 1 (f0409634: ОВП / валютная позиция)",
    2: "Источник 2 (calypso: marketdata + securities positions)",
    3: "Источник 3 (cbonds: emissions + stocks)",
    4: "Источник 4 (calypso: live trades + mortgage amortization)",
    0: "Прочие таблицы",
}

EXPECTED_COLUMNS_BY_TABLE: Dict[str, List[str]] = {
    "f0409634": (
        "adb_id adb_update_timestamp pos_date cur_name cur_code cb_rate "
        "balance_position_cur deriv_position_cur reserve_position_cur "
        "bal_total_cap_prc bal_total_limit urg_pfi_curr urg_other_curr "
        "urg_h_risk_curr urg_insgn_curr ovp_total_cap_prc ovp_total_limit "
        "capital ovp_base_cap_curr ovp_msfo_corr_curr corr_base_cap_curr "
        "ovp_main_cap_curr corr_main_cap_curr ovp_own_cap_curr corr_own_cap_curr "
        "insertdate"
    ).split(),
    "allcurvesquotes": (
        "batch_ref rep_part_num value_date itemtype source name quotetype date "
        "ask bid mid close low high last isin bb_unique reuters oper_date"
    ).split(),
    "livetrades": (
        "batch_ref rep_part_num value_date trade_id product_id product_type "
        "product_extendedtype product_subtype tradestatus quantity book trade_date "
        "book_legal_entity vtb_pricername counterparty_short_name maturity_date "
        "trade_currency notional_currency product_description "
        "trade_keyword_sourcesystemid npv npv_base oper_date"
    ).split(),
    "mortage_amortization": (
        "batch_ref rep_part_num value_date position_date calypso_id "
        "amortization_date amortization_contractual amortization_modelled "
        "oper_date processed_ts"
    ).split(),
    "securities_positions": (
        "batch_ref rep_part_num value_date position_id book product_type "
        "product_code_isin product_code_bb_unique position_quantity "
        "product_description trade_currency vtb_nominal current_notional "
        "quote_name contract_size contract_expiry contract_exchange contract_name "
        "amortizing_structure counterparty_short_name maturity_date "
        "underlying_product_code_isin processing_org_short_name trade_settle_date "
        "vtb_strike vtb_underlying_quotetype vtb_future_contract_ctd_isin "
        "vtb_future_contract_ctd_maturity_date vtb_future_contract_ctd_current_rate "
        "settle_cur underlying_security vtb_bond_coupon_type "
        "vtb_bond_coupon_next_change_date vtb_bond_nearest_offer_date "
        "vtb_bond_nearest_offer_type issuer_attr_inn issuer_attr_siebel_code "
        "issuer_attr_ogress_code issuer vtb_mdi_usage_dis vtb_mdi_usage_for "
        "vtb_mdi_usage_vol vtb_cb_assets vtb_cb_liabilities "
        "vtb_commodity_resetquotename trade_price vtb_sg_ctd_factor "
        "vtb_underlying_price is_buy_sell security_name issuer_full_name "
        "book_legal_entity quantity current_face_value nominal "
        "pricer_price_bid_vd coupon coupon_frequency coupon_type next_coupon_date "
        "vtb_underlying_quotename pricer_price_ask_vd oper_date processed_ts "
        "partition_val"
    ).split(),
    "cbonds_stocks": (
        "id announced_volume begin_circulation_micex blue_chips currency "
        "emitent_id emitent_inn emitent_name_eng emitent_name_rus "
        "end_circulation_micex free_float isin join_other join_other_date "
        "join_other_id kind_id kod_micex micex nominal_price number_of_emission "
        "state_reg_number stock_full_name_eng stock_full_name_rus "
        "stock_name_eng stock_name_rus updating_date date_of_registration "
        "conversion_ratio row_hash operdate country_id country_name_eng "
        "country_name_rus country_region_id country_subregion_id created_at "
        "currency_name cusip depositary_emitents_id description_eng "
        "description_rus emitent_full_name_eng emitent_full_name_rus emitent_lei "
        "emitent_registration_country_eng emitent_registration_country_id "
        "emitent_registration_country_rus innovation_sector_begin_date "
        "innovation_sector_end_date innovation_sector_flag sedol "
        "source_created_at source_updated_at underlying_stocks_full_id wkn cfi "
        "cbr_code"
    ).split(),
    "cbonds_emissions": """
        all_bond_types announced_volume_new bbgid bbgid_ticker bbgid_144a
        bbgid_composite bond_type cfi_code cfi_code_144a convertable
        coupon_type_id cupon_eng cupon_period cupon_rus currency_id
        currency_name cusip_144a cusip_regs date_of_end_placing
        date_of_start_circulation date_of_start_placing document_eng
        document_rus early_redemption_date emission_cupon_basis_id
        emission_cupon_basis_title emission_emitent_id emitent_country
        emitent_country_region_id emitent_country_subregion_id emitent_id
        emitent_name_eng emitent_name_rus eurobonds_nominal floating_rate
        formal_emitent_id for_qualified_investors guaranteed_bonds guarantor_id
        guarantor_name_eng id indexation_eng indexation_rus integral_multiple
        isin_code isin_code_144a isin_code_3 kind_id kind_name_eng kind_name_rus
        margin maturity_date micex_shortname mortgage_bonds nominal_price
        number_of_emission number_of_emission_eng offert_date
        outstanding_nominal_price perpetual placed_volume precision_emission
        reference_rate_id registration_date remaining_outstand_amount
        restructing restructing_date secured_debt sedol settlement_date
        state_reg_number status_id structured_note subkind_id subordinated_debt
        update_time updating_date vid_id agents_eng agents_rus
        amortization_schedule_eng auction_type_id auction_type_name_eng
        auction_type_name_rus bond_class bond_issue_form
        bond_issue_form_name_eng bond_issue_form_name_rus bond_rank
        bond_rank_name_eng bond_rank_name_rus book_closing_date book_opening_date
        cbrf_listing_lombard_last_date_date cdo_bond common_code
        common_code_144a conversion_date convertible_until convert_cond_eng
        convert_cond_rus coupon_type_name_eng coupon_type_name_rus cup
        curr_coupon_date curr_coupon_rate curr_coupon_sum cutoff_price
        cutoff_yield dcc_code dcc_code_144a decision_date delay_days
        dual_currency_bond emission_cbr_code emission_coupon_rate
        emission_wkn_code emission_wkn_code_144a emitent_adress_eng
        emitent_adress_rus emitent_branch_id emitent_branch_name_eng
        emitent_branch_name_rus emitent_country_name_eng emitent_country_name_rus
        emitent_email emitent_full_name_eng emitent_full_name_rus emitent_inn
        emitent_inn_ua emitent_maxratings_msf_foreign_currency
        emitent_maxratings_msf_local_currency emitent_phone emitent_reg_form_id
        emitent_reg_form_name_eng emitent_reg_form_name_rus emitent_site_eng
        emitent_site_rus emitent_type emitent_type_name_eng emitent_type_name_rus
        first_coupon_end floor foreign_bond formal_emitent_branch_id
        formal_emitent_country formal_emitent_name_eng formal_emitent_name_rus
        formal_emitent_reg_form_id formal_emitent_type geography_breakdown_eng
        gov_program_registration_date gov_program_state_reg_number green_bonds
        has_default has_tap_issue high_coupon_guidance high_yield_guidance
        income_of_primary_placing indexation_type indexation_type_name_eng
        indexation_type_name_rus initial_placement_volume initial_premium
        investors_type_eng investors_type_rus issue_form_id
        issue_form_name_eng issue_form_name_rus lock_up low_coupon_guidance
        low_yield_guidance maturity_period_initial more_eng more_rus ndc_code
        next_replacing_amount next_replacing_date nkd_calc_types_id
        nkd_calc_types_name_eng nkd_calc_types_name_rus number_of_emission_rus
        number_of_trades_on_issue_date offert_date_call offert_date_put
        offert_eng offert_rus order_book outstanding_volume
        payment_currency_id payment_currency_name pik placed_volume_new
        placing_type_id placing_type_name_eng placing_type_name_rus
        price_of_primary_placing private_issue private_offering_id
        private_offering_name_eng private_offering_name_rus purpose_eng
        qgc_rewrite_type rating_emission_1055 rating_emission_1055_date
        rating_emission_1070 rating_emission_1070_date rating_emission_2512
        rating_emission_2512_date rating_emitent_foreign_1055
        rating_emitent_foreign_1055_date rating_emitent_foreign_1070
        rating_emitent_foreign_1070_date rating_emitent_foreign_2512
        rating_emitent_foreign_2512_date rating_emitent_national_1055
        rating_emitent_national_1055_date rating_emitent_national_1070
        rating_emitent_national_1070_date rating_emitent_national_2512
        rating_emitent_national_2512_date redemption_linked redemption_price
        reference_rate_name_eng reference_rate_name_rus reg_s
        report_registration_date restructing_more_eng restructing_more_rus
        resumption_date retail_bond securitisation serial_of_emission
        serial_of_emission_eng settlement_duration show_ru spread_mid_swaps
        spread_us_treasures sp_category_id sp_category_name_eng sp_type_id
        sp_type_name_eng ss_current_trading_grounds ss_tg_countries
        ss_tg_qlists ss_trading_grounds status_issue_form
        status_issue_form_name_eng status_issue_form_name_rus status_name_eng
        status_name_rus subkind_name_eng subkind_name_rus sukuk_bond
        suspension_date trace_eligible_securites tradings_duration
        tradings_indicative_price tradings_maxdate tradings_yield_effect
        trading_grounds_full_eng trading_grounds_full_rus
        trading_ground_name_eng trading_ground_name_rus underlying_class_id
        underlying_class_name_eng underlying_instrument_code underlying_ticker
        usd_volume variable_rate_type_id vid_name_eng vid_name_rus operdate
        row_hash
    """.split(),
}

COLUMN_KINDS_BY_TABLE: Dict[str, Dict[str, str]] = {
    "f0409634": {
        "adb_id": "numeric", "adb_update_timestamp": "date", "pos_date": "date",
        "cur_name": "string_code", "cur_code": "string_code", "cb_rate": "numeric",
        "balance_position_cur": "numeric", "deriv_position_cur": "numeric",
        "reserve_position_cur": "numeric", "bal_total_cap_prc": "numeric",
        "bal_total_limit": "numeric", "urg_pfi_curr": "numeric",
        "urg_other_curr": "numeric", "urg_h_risk_curr": "numeric",
        "urg_insgn_curr": "numeric", "ovp_total_cap_prc": "numeric",
        "ovp_total_limit": "numeric", "capital": "numeric",
        "ovp_base_cap_curr": "numeric", "ovp_msfo_corr_curr": "numeric",
        "corr_base_cap_curr": "numeric", "ovp_main_cap_curr": "numeric",
        "corr_main_cap_curr": "numeric", "ovp_own_cap_curr": "numeric",
        "corr_own_cap_curr": "numeric", "insertdate": "date",
    },
    "allcurvesquotes": {
        "batch_ref": "string_code", "rep_part_num": "numeric", "value_date": "date",
        "itemtype": "text", "source": "text", "name": "string_code",
        "quotetype": "text", "date": "date", "ask": "numeric", "bid": "numeric",
        "mid": "numeric", "close": "numeric", "low": "numeric", "high": "numeric",
        "last": "numeric", "isin": "isin", "bb_unique": "text", "reuters": "text",
        "oper_date": "date",
    },
    "livetrades": {
        "batch_ref": "string_code", "rep_part_num": "numeric", "value_date": "date",
        "trade_id": "numeric", "product_id": "numeric", "product_type": "text",
        "product_extendedtype": "text", "product_subtype": "text",
        "tradestatus": "text", "quantity": "numeric", "book": "string_code",
        "trade_date": "date", "book_legal_entity": "string_code",
        "vtb_pricername": "text", "counterparty_short_name": "text",
        "maturity_date": "date", "trade_currency": "currency",
        "notional_currency": "currency", "product_description": "text",
        "trade_keyword_sourcesystemid": "string_code", "npv": "numeric",
        "npv_base": "numeric", "oper_date": "date",
    },
    "mortage_amortization": {
        "batch_ref": "string_code", "rep_part_num": "numeric", "value_date": "date",
        "position_date": "date", "calypso_id": "numeric",
        "amortization_date": "date", "amortization_contractual": "numeric",
        "amortization_modelled": "numeric", "oper_date": "date",
        "processed_ts": "date",
    },
    "securities_positions": {
        "batch_ref": "string_code", "rep_part_num": "numeric", "value_date": "date",
        "position_id": "numeric", "book": "string_code", "product_type": "text",
        "product_code_isin": "isin", "product_code_bb_unique": "text",
        "position_quantity": "numeric", "product_description": "text",
        "trade_currency": "currency", "vtb_nominal": "numeric",
        "current_notional": "numeric", "quote_name": "text",
        "contract_size": "numeric", "contract_expiry": "date",
        "contract_exchange": "text", "contract_name": "text",
        "amortizing_structure": "text", "counterparty_short_name": "text",
        "maturity_date": "date", "underlying_product_code_isin": "isin",
        "processing_org_short_name": "text", "trade_settle_date": "date",
        "vtb_strike": "numeric", "vtb_underlying_quotetype": "text",
        "vtb_future_contract_ctd_isin": "isin",
        "vtb_future_contract_ctd_maturity_date": "date",
        "vtb_future_contract_ctd_current_rate": "numeric",
        "settle_cur": "currency", "underlying_security": "text",
        "vtb_bond_coupon_type": "text",
        "vtb_bond_coupon_next_change_date": "date",
        "vtb_bond_nearest_offer_date": "date",
        "vtb_bond_nearest_offer_type": "text",
        "issuer_attr_inn": "string_code", "issuer_attr_siebel_code": "string_code",
        "issuer_attr_ogress_code": "string_code", "issuer": "text",
        "vtb_mdi_usage_dis": "text", "vtb_mdi_usage_for": "text",
        "vtb_mdi_usage_vol": "text",  
        "vtb_cb_assets": "numeric",
        "vtb_cb_liabilities": "numeric", "vtb_commodity_resetquotename": "text",
        "trade_price": "numeric", "vtb_sg_ctd_factor": "numeric",
        "vtb_underlying_price": "numeric", "is_buy_sell": "numeric",
        "security_name": "text", "issuer_full_name": "text",
        "book_legal_entity": "string_code", "quantity": "numeric",
        "current_face_value": "numeric", "nominal": "numeric",
        "pricer_price_bid_vd": "numeric", "coupon": "numeric",
        "coupon_frequency": "text", "coupon_type": "text",
        "next_coupon_date": "date", "vtb_underlying_quotename": "text",
        "pricer_price_ask_vd": "numeric", "oper_date": "date",
        "processed_ts": "date", "partition_val": "text",
    },
    "cbonds_stocks": {
        "id": "numeric", "announced_volume": "numeric",
        "begin_circulation_micex": "date", "blue_chips": "numeric",
        "currency": "numeric", "emitent_id": "numeric", "emitent_inn": "string_code",
        "emitent_name_eng": "text", "emitent_name_rus": "text",
        "end_circulation_micex": "date", "free_float": "numeric",
        "isin": "string_code", "join_other": "numeric", "join_other_date": "date",
        "join_other_id": "numeric", "kind_id": "numeric", "kod_micex": "text",
        "micex": "numeric", "nominal_price": "numeric",
        "number_of_emission": "text", "state_reg_number": "string_code",
        "stock_full_name_eng": "text", "stock_full_name_rus": "text",
        "stock_name_eng": "text", "stock_name_rus": "text",
        "updating_date": "date", "date_of_registration": "date",
        "conversion_ratio": "numeric", "row_hash": "string_code",
        "operdate": "date", "country_id": "numeric", "country_name_eng": "text",
        "country_name_rus": "text", "country_region_id": "numeric",
        "country_subregion_id": "numeric", "created_at": "date",
        "currency_name": "text", "cusip": "string_code",
        "depositary_emitents_id": "numeric", "description_eng": "text",
        "description_rus": "text", "emitent_full_name_eng": "text",
        "emitent_full_name_rus": "text", "emitent_lei": "string_code",
        "emitent_registration_country_eng": "text",
        "emitent_registration_country_id": "numeric",
        "emitent_registration_country_rus": "text",
        "innovation_sector_begin_date": "date",
        "innovation_sector_end_date": "date", "innovation_sector_flag": "numeric",
        "sedol": "string_code", "source_created_at": "date",
        "source_updated_at": "date", "underlying_stocks_full_id": "numeric",
        "wkn": "string_code", "cfi": "string_code", "cbr_code": "string_code",
    },
    "cbonds_emissions": {
        "isin_code": "isin", "isin_code_144a": "isin", "isin_code_3": "string_code",
        "cfi_code": "string_code", "cfi_code_144a": "string_code",
        "cusip_144a": "string_code", "cusip_regs": "string_code",
        "state_reg_number": "string_code", "gov_program_state_reg_number": "string_code",
        "common_code": "string_code", "common_code_144a": "string_code",
        "dcc_code": "string_code", "dcc_code_144a": "string_code",
        "emission_cbr_code": "string_code", "emission_wkn_code": "string_code",
        "emission_wkn_code_144a": "string_code", "ndc_code": "string_code",
        "sedol": "string_code", "reg_s": "string_code", "row_hash": "string_code",
        "all_bond_types": "text", "number_of_emission": "text",
        "number_of_emission_eng": "text", "number_of_emission_rus": "text",
        "micex_shortname": "text", "cup": "text", "currency_name": "text",
        "payment_currency_name": "text", "emitent_type": "numeric",
        "formal_emitent_type": "numeric", "bond_type": "numeric",
        "bond_class": "numeric", "bond_rank": "numeric", "cupon_period": "numeric",
        "floating_rate": "numeric", "margin": "numeric", "floor": "numeric",
        "perpetual": "numeric", "precision_emission": "numeric",
        "number_of_trades_on_issue_date": "numeric",
    },
}

CRITICAL_COLS_BY_TABLE: Dict[str, Set[str]] = {
    "f0409634": {"adb_id", "pos_date", "cur_name", "cur_code", "insertdate"},
    "allcurvesquotes": {"batch_ref", "value_date", "name", "date", "oper_date"},
    "livetrades": {
        "batch_ref", "value_date", "trade_id", "product_id", "trade_date",
        "trade_currency", "npv", "npv_base", "oper_date",
    },
    "mortage_amortization": {
        "batch_ref", "value_date", "calypso_id", "amortization_date", "oper_date",
    },
    "securities_positions": {
        "value_date", "position_id", "book", "product_type",
        "position_quantity", "trade_currency", "oper_date", "processed_ts",
    },
    "cbonds_stocks": {
        "id", "isin", "currency", "emitent_id", "stock_name_eng", "operdate",
    },
    "cbonds_emissions": {
        "id", "isin_code", "currency_id", "emitent_id", "operdate", "row_hash",
    },
}

NON_NEGATIVE_COLS = {"adb_id", "trade_id", "product_id", "rep_part_num", "calypso_id"}
STRING_CODE_COLS = {"isin_code", "account", "dealnumber", "clientcode", "key", "instr_short", "row_hash", "mic", "book", "batch_ref"}
CURRENCY_COLS = {"currency", "dealcurr", "paymentcurrency", "buycurrency", "sellcurrency", "cur", "curr", "nominal_currency", "price_currency", "trade_currency"}
ACCOUNT_COLS = {"account", "cashflowaccount", "demandaccnum", "obligaccnum"}
NUMERIC_OVERRIDE_COLS = {"amount", "volume", "price", "value", "marketvalue", "nominal_value", "quantity", "lot", "npv", "npv_base", "ask", "bid", "mid", "close", "low", "high", "last", "capital", "cb_rate"}
ALLOWED_TECH_DATES = {"1900-01-01", "1970-01-01", "2100-01-01", "5999-12-31", "9999-12-31"}

_NAMED_ENTITY_COLS = {
    "issuer", "clientname", "contragent", "companyname", "name_eng", "name_rus",
    "stock_name_eng", "stock_name_rus", "stock_full_name_eng", "stock_full_name_rus",
    "emitent_name_eng", "emitent_name_rus", "emitent_full_name_eng", "emitent_full_name_rus",
    "security_name", "issuer_full_name", "product_description", "counterparty_short_name",
    "description_eng", "description_rus", "contract_name", "vtb_pricername",
    "quote_name", "vtb_underlying_quotename", "vtb_commodity_resetquotename",
    "country_name_eng", "country_name_rus", "emitent_registration_country_eng",
    "emitent_registration_country_rus", "kod_micex",
    "number_of_emission", "number_of_emission_eng", "number_of_emission_rus",
    "micex_shortname", "emitent_site_eng", "emitent_site_rus", "emitent_email",
}

# 2. Вспомогательные функции

def _detect_source_id(table_name: str) -> int:
    name = str(table_name).lower()
    for pat, sid in SOURCE_PATTERNS:
        if pat in name:
            return sid
    return 0

def _resolve_schema_key(table_name: str) -> Optional[str]:
    name = str(table_name).lower().strip()
    for k in EXPECTED_COLUMNS_BY_TABLE:
        if k in name:
            return k
    return None

_NA_MARKERS = ["", "None", "none", "NONE", "NULL", "null", "NaN", "nan", "N/A", "n/a", '""', "''", "(None)", "(none)"]

def _fix_unparsed_dollar_df(df: pd.DataFrame) -> pd.DataFrame:
    if len(df.columns) == 1 and "$" in str(df.columns[0]):
        raw_header = str(df.columns[0]).replace("\ufeff", "")
        header = [h.strip().strip('"').strip() for h in raw_header.split("$")]
        col_name = df.columns[0]
        split_rows = df[col_name].fillna("").astype(str).apply(lambda s: s.split("$"))
        fixed_data = []
        for row in split_rows:
            cleaned = [str(v).strip().strip('"').strip() for v in row]
            cleaned = cleaned[: len(header)] + [""] * max(0, len(header) - len(cleaned))
            fixed_data.append(cleaned)
        fixed_df = pd.DataFrame(fixed_data, columns=header, index=df.index)
        return fixed_df.replace(_NA_MARKERS, pd.NA)
    return df.replace(_NA_MARKERS, pd.NA)

_DATE_RE = re.compile(r"^(?:\d{4}-\d{2}-\d{2}(?:[T\s]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?|\d{2}\.\d{2}\.\d{4}(?:\s\d{2}:\d{2}(?::\d{2})?)?|\d{8}|\d{10}(?:\.0+)?)$")
_NUMERIC_RE = re.compile(r"^[+-]?(?:\d+(?:[.,]\d+)?|[.,]\d+)(?:[eE][+-]?\d+)?$")
_CURRENCY_RE = re.compile(r"^(?:[A-Z]{3}|\d{3})$")
_ISIN_RE = re.compile(r"^[A-Z]{2}[A-Z0-9]{10}$")
_DIGITS_ONLY_RE = re.compile(r"^\d+$")
_OLB_ACC_RE = re.compile(r"^[A-Za-z0-9*]+$")
_EMPTY_TOKENS = {"", "None", "none", "NONE", "NULL", "null", "NaN", "nan", '""', "''", "(None)", "(none)"}

def _empty_mask(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype(str).str.strip().isin(_EMPTY_TOKENS)

def _infer_col_kind(col_name: str, source_id: int, schema_key: Optional[str] = None) -> str:
    c = str(col_name).lower().strip()
    if schema_key and schema_key in COLUMN_KINDS_BY_TABLE:
        explicit = COLUMN_KINDS_BY_TABLE[schema_key]
        if c in explicit:
            return explicit[c]
    if c in NUMERIC_OVERRIDE_COLS:
        return "numeric"
    if c in ACCOUNT_COLS:
        return "account"
    if c in CURRENCY_COLS or c.endswith(("_curr", "_currency", "_ccy", "currcode")):
        return "currency"
    if c in STRING_CODE_COLS:
        return "string_code"
    if c == "date" or c.endswith(("_date", "date", "_dt", "_dttm", "_timestamp")):
        return "date"
    if c.endswith(("_type", "_name")):
        return "text"
    if c.endswith("_cur") and not c.endswith("_curr"):
        return "numeric"
    if any(c == k or c.endswith(f"_{k}") or c.startswith(f"{k}_") for k in ("id", "num", "amount", "volume", "price", "rate", "balance", "sum", "rub", "usd", "delta", "gamma", "vega", "theta", "rho", "strike", "lot", "go", "lk1", "lk2", "ytm", "yto", "ytc", "nkd")):
        return "numeric"
    return "text"

def _is_critical_col(col_name: str, schema_key: Optional[str]) -> bool:
    if schema_key is None:
        return False
    return str(col_name).lower().strip() in CRITICAL_COLS_BY_TABLE.get(schema_key, set())

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
            sub = s[non_empty]
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
                nums = pd.to_numeric(cleaned[valid_num_mask].str.replace(",", ".", regex=False), errors="coerce")
                bad_sign = nums.lt(0)
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
        
        is_unix = check_sub.str.match(r"^\d{10}(?:\.0+)?$")
        valid_fmt = check_sub[fmt_ok & ~is_unix]
        
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

def _check_table_schema(schema_key: Optional[str], columns: List[str]) -> Tuple[List[str], List[str]]:
    broken = [str(c) for c in columns if str(c).strip() == "" or str(c).startswith("Unnamed:") or re.search(r"\.\d+$", str(c))]
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
    warnings = []
    if missing_regular:
        warnings.append(f"отсутствуют обычные столбцы ({', '.join(missing_regular)})")
    if extra:
        warnings.append(f"обнаружены лишние столбцы ({', '.join(extra)})")
    return missing_critical, warnings

def _validate_table(table_name: str, df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    source_id = _detect_source_id(table_name)
    schema_key = _resolve_schema_key(table_name)

    if "__load_error__" in df.columns:
        err = str(df["__load_error__"].iloc[0])
        return pd.DataFrame(), {
            "source_id": source_id, "total_rows": 0, "removed_rows": 0,
            "row_errors": [f"ошибка чтения файла: {err}"], "schema_warnings": [],
        }

    work_df = _fix_unparsed_dollar_df(df.copy())
    total_rows = len(work_df)

    missing_critical, schema_warnings = _check_table_schema(schema_key, list(work_df.columns))
    if missing_critical:
        reason = f"схема: отсутствует критический столбец ({', '.join(missing_critical)})"
        return pd.DataFrame(columns=work_df.columns), {
            "source_id": source_id, "total_rows": total_rows, "removed_rows": total_rows,
            "row_errors": [reason], "schema_warnings": schema_warnings,
        }

    broken_headers = [c for c in work_df.columns if str(c).startswith("Unnamed:") or re.search(r"\.\d+$", str(c))]
    if broken_headers:
        work_df = work_df.drop(columns=broken_headers)

    empty_masks = {c: _empty_mask(work_df[c]) for c in work_df.columns}
    empty_cols = [c for c, mask in empty_masks.items() if mask.all()]
    if empty_cols:
        work_df = work_df.drop(columns=empty_cols)
        for c in empty_cols:
            empty_masks.pop(c, None)

    error_reasons_by_idx: Dict[int, List[str]] = {}
    any_invalid = pd.Series(False, index=work_df.index)

    for col in work_df.columns:
        s = work_df[col]
        empty = empty_masks[col]
        kind = _infer_col_kind(str(col), source_id, schema_key)
        is_crit = _is_critical_col(str(col), schema_key)

        if is_crit and empty.any():
            any_invalid |= empty
            for pos in work_df.index[empty]:
                error_reasons_by_idx.setdefault(int(pos), []).append(f"пропуск в критическом поле '{col}'")

        bad_fmt = _invalid_series_mask(s, kind, source_id, empty)
        if bad_fmt.any():
            any_invalid |= bad_fmt
            for pos in work_df.index[bad_fmt]:
                val_str = str(s.loc[pos]).strip()
                error_reasons_by_idx.setdefault(int(pos), []).append(f"{col}: некорректное значение ({val_str})")

    row_errors = [f"стр. {pos + 2}: {'; '.join(error_reasons_by_idx[pos])}" for pos in sorted(error_reasons_by_idx)]
    clean_df = work_df[~any_invalid].copy()
    removed_rows = total_rows - len(clean_df)

    return clean_df, {
        "source_id": source_id, "total_rows": total_rows, "removed_rows": removed_rows,
        "row_errors": row_errors, "schema_warnings": schema_warnings,
    }

# 3. Публичная функция

def process_rr_calc(process_id: str, tables: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, List[str]]:
    """Валидация данных для сервиса rr_calc (рыночный риск)."""
    logs = [f"[{process_id}] Запуск валидации данных модуля rr_calc"]

    if not tables:
        logs.append(f"[{process_id}] Входные таблицы не найдены.")
        return pd.DataFrame(columns=["Метрика", "Сумма (RUB)"]), logs

    stats_by_source = {sid: {"tables": 0, "total": 0, "removed": 0, "details": []} for sid in SOURCE_TITLES}

    for tbl_name, tbl_df in sorted(tables.items()):
        _, info = _validate_table(tbl_name, tbl_df)
        sid = info["source_id"]
        if sid not in stats_by_source:
            sid = 0

        stats_by_source[sid]["tables"] += 1
        stats_by_source[sid]["total"] += info["total_rows"]
        stats_by_source[sid]["removed"] += info["removed_rows"]

        for warn in info.get("schema_warnings", []):
            stats_by_source[sid]["details"].append(f"  [Схема] {tbl_name}: {warn}")

        if info["row_errors"]:
            stats_by_source[sid]["details"].append(f"  Таблица '{tbl_name}' (удалено {info['removed_rows']} из {info['total_rows']}):")
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
        logs.append(f"{SOURCE_TITLES[sid]}: таблиц={st['tables']}, всего строк={st['total']}, удалено={st['removed']}, валидных={st['total'] - st['removed']}")
        logs.extend(st["details"])

    valid_all = total_all - removed_all
    logs.append(f"[{process_id}] Итого по rr_calc: всего={total_all}, валидных={valid_all}, удалено={removed_all}")

    summary_df = pd.DataFrame([
        {"Метрика": "rr_calc: Всего проверено строк", "Сумма (RUB)": float(total_all)},
        {"Метрика": "rr_calc: Валидных строк", "Сумма (RUB)": float(valid_all)},
        {"Метрика": "rr_calc: Отбраковано строк", "Сумма (RUB)": float(removed_all)},
    ])
    return summary_df, logs