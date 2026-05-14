def parse_comma_sep_str(comma_sep_str: str) -> list[str]:
    splitted_strs = comma_sep_str.split(',')
    striped_strs_map = map(lambda h: h.strip(), splitted_strs)
    truthy_strs_filter = filter(lambda h: bool(h), striped_strs_map)
    return list(truthy_strs_filter)
