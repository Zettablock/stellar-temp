from stellar_sdk.scval import to_symbol
from stellar_sdk.xdr import SCValType, LedgerEntry


def contract_balance_from_contract_data(ledger_entry: LedgerEntry):
    contract_data = ledger_entry.data.contract_data
    if not contract_data:
        return None, None, False

    if contract_data.contract.contract_id is None:
        return None, None, False

    key_enum_vec_ptr = contract_data.key.vec
    if key_enum_vec_ptr is None:
        return None, None, False

    key_enum_vec = key_enum_vec_ptr.sc_vec
    if len(key_enum_vec) != 2 or not key_enum_vec[0] == to_symbol("Balance"):
        return None, None, False

    sc_address = key_enum_vec[1].address
    if not sc_address:
        return None, None, False

    holder = sc_address.contract_id
    if not holder:
        return None, None, False

    balance_map_ptr, ok = contract_data.val.map
    if balance_map_ptr is None:
        return None, None, False

    balance_map = balance_map_ptr.sc_map
    if len(balance_map) != 3:
        return None, None, False

    key_sym = balance_map[0].key.sym
    if not key_sym or key_sym != "amount":
        return None, None, False

    key_sym = balance_map[1].key.sym
    if (
            not key_sym
            or key_sym != "authorized"
            or balance_map[1].val.type != SCValType.SCV_BOOL
    ):
        return None, None, False

    key_sym = balance_map[2].key.sym
    if (
            not key_sym
            or key_sym != "clawback"
            or balance_map[2].val.type != SCValType.SCV_BOOL
    ):
        return None, None, False

    amount = balance_map[0].val.i128
    if not amount:
        return None, None, False

    if int(amount.hi) < 0:
        return None, None, False

    amt = (int(amount.hi) << 64) + int(amount.lo)
    return holder, amt, True


if __name__ == "__main__":
    xdr = "AAAAAwAAAAAAAAACAAAAAwMZfscAAAAAAAAAAPexvDFqySbwcBDHMsmW8ilJL7J23or9tB2Cfm52mKP7AAAAAGzhhGoDEgoiAAADhwAAAAIAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAMAAAAAAxl+xQAAAABmYct7AAAAAAAAAAEDGX7HAAAAAAAAAAD3sbwxaskm8HAQxzLJlvIpSS+ydt6K/bQdgn5udpij+wAAAABs4YRqAxIKIgAAA4gAAAACAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAADAAAAAAMZfscAAAAAZmHLhwAAAAAAAAABAAAADAAAAAMDGX7FAAAABgAAAAAAAAAB6wqp2NYleWkC+pvmNBKR3gd+jdUjpzeORqSmFS2oGDsAAAAQAAAAAQAAAAIAAAAPAAAAB1Jlc0RhdGEAAAAAEgAAAAGt785ZruUpaPdgYdSUwlJbdWWfpClqZfSZ7ynlZHfklgAAAAEAAAARAAAAAQAAAAcAAAAPAAAABmJfcmF0ZQAAAAAACgAAAAAAAAAAAAAAADwAGnUAAAAPAAAACGJfc3VwcGx5AAAACgAAAAAAAAAAAAALp1WK/hsAAAAPAAAAD2JhY2tzdG9wX2NyZWRpdAAAAAAKAAAAAAAAAAAAAAADm/z7PgAAAA8AAAAGZF9yYXRlAAAAAAAKAAAAAAAAAAAAAAAAPDMYgQAAAA8AAAAIZF9zdXBwbHkAAAAKAAAAAAAAAAAAAAn6JR88qgAAAA8AAAAGaXJfbW9kAAAAAAAKAAAAAAAAAAAAAAAAPTjCYgAAAA8AAAAJbGFzdF90aW1lAAAAAAAABQAAAABmYct7AAAAAAAAAAEDGX7HAAAABgAAAAAAAAAB6wqp2NYleWkC+pvmNBKR3gd+jdUjpzeORqSmFS2oGDsAAAAQAAAAAQAAAAIAAAAPAAAAB1Jlc0RhdGEAAAAAEgAAAAGt785ZruUpaPdgYdSUwlJbdWWfpClqZfSZ7ynlZHfklgAAAAEAAAARAAAAAQAAAAcAAAAPAAAABmJfcmF0ZQAAAAAACgAAAAAAAAAAAAAAADwAGpoAAAAPAAAACGJfc3VwcGx5AAAACgAAAAAAAAAAAAALqaynCUoAAAAPAAAAD2JhY2tzdG9wX2NyZWRpdAAAAAAKAAAAAAAAAAAAAAADm/7SmwAAAA8AAAAGZF9yYXRlAAAAAAAKAAAAAAAAAAAAAAAAPDMYuAAAAA8AAAAIZF9zdXBwbHkAAAAKAAAAAAAAAAAAAAn6JR88qgAAAA8AAAAGaXJfbW9kAAAAAAAKAAAAAAAAAAAAAAAAPTjH6QAAAA8AAAAJbGFzdF90aW1lAAAAAAAABQAAAABmYcuHAAAAAAAAAAMDGX7DAAAABgAAAAAAAAAB6wqp2NYleWkC+pvmNBKR3gd+jdUjpzeORqSmFS2oGDsAAAAQAAAAAQAAAAIAAAAPAAAACEVtaXNEYXRhAAAAAwAAAAMAAAABAAAAEQAAAAEAAAACAAAADwAAAAVpbmRleAAAAAAAAAoAAAAAAAAAAAAAAAAAXUO1AAAADwAAAAlsYXN0X3RpbWUAAAAAAAAFAAAAAGZhy28AAAAAAAAAAQMZfscAAAAGAAAAAAAAAAHrCqnY1iV5aQL6m+Y0EpHeB36N1SOnN45GpKYVLagYOwAAABAAAAABAAAAAgAAAA8AAAAIRW1pc0RhdGEAAAADAAAAAwAAAAEAAAARAAAAAQAAAAIAAAAPAAAABWluZGV4AAAAAAAACgAAAAAAAAAAAAAAAABdQ8sAAAAPAAAACWxhc3RfdGltZQAAAAAAAAUAAAAAZmHLhwAAAAAAAAADAxl+xQAAAAYAAAAAAAAAAesKqdjWJXlpAvqb5jQSkd4Hfo3VI6c3jkakphUtqBg7AAAAEAAAAAEAAAACAAAADwAAAAlQb3NpdGlvbnMAAAAAAAASAAAAAAAAAAD3sbwxaskm8HAQxzLJlvIpSS+ydt6K/bQdgn5udpij+wAAAAEAAAARAAAAAQAAAAMAAAAPAAAACmNvbGxhdGVyYWwAAAAAABEAAAABAAAAAQAAAAMAAAABAAAACgAAAAAAAAAAAAAGDG7pHpgAAAAPAAAAC2xpYWJpbGl0aWVzAAAAABEAAAABAAAAAQAAAAMAAAABAAAACgAAAAAAAAAAAAAFWg1UCRgAAAAPAAAABnN1cHBseQAAAAAAEQAAAAEAAAAAAAAAAAAAAAEDGX7HAAAABgAAAAAAAAAB6wqp2NYleWkC+pvmNBKR3gd+jdUjpzeORqSmFS2oGDsAAAAQAAAAAQAAAAIAAAAPAAAACVBvc2l0aW9ucwAAAAAAABIAAAAAAAAAAPexvDFqySbwcBDHMsmW8ilJL7J23or9tB2Cfm52mKP7AAAAAQAAABEAAAABAAAAAwAAAA8AAAAKY29sbGF0ZXJhbAAAAAAAEQAAAAEAAAABAAAAAwAAAAEAAAAKAAAAAAAAAAAAAAYOxgUpxwAAAA8AAAALbGlhYmlsaXRpZXMAAAAAEQAAAAEAAAABAAAAAwAAAAEAAAAKAAAAAAAAAAAAAAVaDVQJGAAAAA8AAAAGc3VwcGx5AAAAAAARAAAAAQAAAAAAAAAAAAAAAwMZfsUAAAAGAAAAAAAAAAGt785ZruUpaPdgYdSUwlJbdWWfpClqZfSZ7ynlZHfklgAAABAAAAABAAAAAgAAAA8AAAAHQmFsYW5jZQAAAAASAAAAAesKqdjWJXlpAvqb5jQSkd4Hfo3VI6c3jkakphUtqBg7AAAAAQAAABEAAAABAAAAAwAAAA8AAAAGYW1vdW50AAAAAAAKAAAAAAAAAAAAAAGrHTvCIQAAAA8AAAAKYXV0aG9yaXplZAAAAAAAAAAAAAEAAAAPAAAACGNsYXdiYWNrAAAAAAAAAAAAAAAAAAAAAQMZfscAAAAGAAAAAAAAAAGt785ZruUpaPdgYdSUwlJbdWWfpClqZfSZ7ynlZHfklgAAABAAAAABAAAAAgAAAA8AAAAHQmFsYW5jZQAAAAASAAAAAesKqdjWJXlpAvqb5jQSkd4Hfo3VI6c3jkakphUtqBg7AAAAAQAAABEAAAABAAAAAwAAAA8AAAAGYW1vdW50AAAAAAAKAAAAAAAAAAAAAAGteFIoOAAAAA8AAAAKYXV0aG9yaXplZAAAAAAAAAAAAAEAAAAPAAAACGNsYXdiYWNrAAAAAAAAAAAAAAAAAAAAAwMZfsMAAAAGAAAAAAAAAAHrCqnY1iV5aQL6m+Y0EpHeB36N1SOnN45GpKYVLagYOwAAABAAAAABAAAAAgAAAA8AAAAIVXNlckVtaXMAAAARAAAAAQAAAAIAAAAPAAAACnJlc2VydmVfaWQAAAAAAAMAAAADAAAADwAAAAR1c2VyAAAAEgAAAAAAAAAA97G8MWrJJvBwEMcyyZbyKUkvsnbeiv20HYJ+bnaYo/sAAAABAAAAEQAAAAEAAAACAAAADwAAAAdhY2NydWVkAAAAAAoAAAAAAAAAAAAAAABzN52JAAAADwAAAAVpbmRleAAAAAAAAAoAAAAAAAAAAAAAAAAAXUO1AAAAAAAAAAEDGX7HAAAABgAAAAAAAAAB6wqp2NYleWkC+pvmNBKR3gd+jdUjpzeORqSmFS2oGDsAAAAQAAAAAQAAAAIAAAAPAAAACFVzZXJFbWlzAAAAEQAAAAEAAAACAAAADwAAAApyZXNlcnZlX2lkAAAAAAADAAAAAwAAAA8AAAAEdXNlcgAAABIAAAAAAAAAAPexvDFqySbwcBDHMsmW8ilJL7J23or9tB2Cfm52mKP7AAAAAQAAABEAAAABAAAAAgAAAA8AAAAHYWNjcnVlZAAAAAAKAAAAAAAAAAAAAAAAdBbeAwAAAA8AAAAFaW5kZXgAAAAAAAAKAAAAAAAAAAAAAAAAAF1DywAAAAAAAAADAxl+xQAAAAEAAAAA97G8MWrJJvBwEMcyyZbyKUkvsnbeiv20HYJ+bnaYo/sAAAABVVNEQwAAAAA7mRE4Dv6Yi6CokA6xz+RPNm99vpRr7QdyQPf2JN8VxQAAAAJbFmYXf/////////8AAAABAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEDGX7HAAAAAQAAAAD3sbwxaskm8HAQxzLJlvIpSS+ydt6K/bQdgn5udpij+wAAAAFVU0RDAAAAADuZETgO/piLoKiQDrHP5E82b32+lGvtB3JA9/Yk3xXFAAAAAAAAAAB//////////wAAAAEAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAMDGX7HAAAAAAAAAAD3sbwxaskm8HAQxzLJlvIpSS+ydt6K/bQdgn5udpij+wAAAABs4YRqAxIKIgAAA4gAAAACAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAADAAAAAAMZfscAAAAAZmHLhwAAAAAAAAABAxl+xwAAAAAAAAAA97G8MWrJJvBwEMcyyZbyKUkvsnbeiv20HYJ+bnaYo/sAAAAAbOGljwMSCiIAAAOIAAAAAgAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAwAAAAADGX7HAAAAAGZhy4cAAAAAAAAAAQAAAAAAAAACAAAAAAAAAAHrCqnY1iV5aQL6m+Y0EpHeB36N1SOnN45GpKYVLagYOwAAAAEAAAAAAAAAAwAAAA8AAAARc3VwcGx5X2NvbGxhdGVyYWwAAAAAAAASAAAAAa3vzlmu5Slo92Bh1JTCUlt1ZZ+kKWpl9JnvKeVkd+SWAAAAEgAAAAAAAAAA97G8MWrJJvBwEMcyyZbyKUkvsnbeiv20HYJ+bnaYo/sAAAAQAAAAAQAAAAIAAAAKAAAAAAAAAAAAAAACWxZmFwAAAAoAAAAAAAAAAAAAAAJXHAsvAAAAAAAAAAGt785ZruUpaPdgYdSUwlJbdWWfpClqZfSZ7ynlZHfklgAAAAEAAAAAAAAABAAAAA8AAAAIdHJhbnNmZXIAAAASAAAAAAAAAAD3sbwxaskm8HAQxzLJlvIpSS+ydt6K/bQdgn5udpij+wAAABIAAAAB6wqp2NYleWkC+pvmNBKR3gd+jdUjpzeORqSmFS2oGDsAAAAOAAAAPVVTREM6R0E1WlNFSllCMzdKUkM1QVZDSUE1TU9QNFJIVE0zMzVYMktHWDNJSE9KQVBQNVJFMzRLNEtaVk4AAAAAAAAKAAAAAAAAAAAAAAACWxZmFwAAABEAAAABAAAAAwAAAA8AAAAKY29sbGF0ZXJhbAAAAAAAEQAAAAEAAAABAAAAAwAAAAEAAAAKAAAAAAAAAAAAAAYOxgUpxwAAAA8AAAALbGlhYmlsaXRpZXMAAAAAEQAAAAEAAAABAAAAAwAAAAEAAAAKAAAAAAAAAAAAAAVaDVQJGAAAAA8AAAAGc3VwcGx5AAAAAAARAAAAAQAAAAAAAAAA"

    ledger_entry = LedgerEntry.from_xdr(xdr)

    print(ledger_entry)

    print(contract_balance_from_contract_data(ledger_entry))
