CREATE INDEX munigeo_street_iname_fi_idx ON munigeo_street (UPPER(name_fi) text_pattern_ops);
CREATE INDEX munigeo_street_iname_sv_idx ON munigeo_street (UPPER(name_sv) text_pattern_ops);
