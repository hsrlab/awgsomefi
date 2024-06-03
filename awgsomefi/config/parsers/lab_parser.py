def parse_lab(raw_config):
    lab_config = raw_config['lab']
    lab_name = lab_config['lab_active']
    return lab_config.get(lab_name)
