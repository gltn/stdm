/* This SQL script populates the cb_relevant_authority table and should be run only after
   running the configuration wizard */

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Gobabis', 'GOBBIS', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
	WHERE ra.value = 'Municipality Council' AND region.value = 'Omaheke';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Grootfontein', 'GRTFIN', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Municipality Council' AND region.value = 'Otjozondjupa';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Henties Bay', 'HENTAY', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Municipality Council' AND region.value = 'Erongo';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Keetmanshoop', 'KETMOP', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Municipality Council' AND region.value = 'Karas';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Mariental', 'MARNAL', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Municipality Council' AND region.value = 'Hardap';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Okahandja', 'OKHNJA', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Municipality Council' AND region.value = 'Otjozondjupa';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Omaruru', 'OMARRU', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Municipality Council' AND region.value = 'Erongo';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Otjiwarongo', 'OTJWGO', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Municipality Council' AND region.value = 'Otjozondjupa';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Outjo', 'OUTJOX', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Municipality Council' AND region.value = 'Kunene';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Swakopmund', 'SWKPND', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Municipality Council' AND region.value = 'Erongo';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Tsumeb', 'TSUMEB', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Municipality Council' AND region.value = 'Oshikoto';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Walvis Bay', 'WALVAY', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Municipality Council' AND region.value = 'Erongo';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Windhoek', 'WINDEK', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Municipality Council' AND region.value = 'Khomas';

--TOWN COUNCIL:

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Arandis', 'ARNDIS', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Erongo';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Aranos', 'ARANOS', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Hardap';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Eenhana', 'EENHNA', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Ohangwena';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Helao Nafidi', 'HELNDI', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Ohangwena';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Karasburg', 'KARSRG', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Karas';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Karibib', 'KARBIB', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Erongo';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Katima Mulilo', 'KATMLO', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Zambezi';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Khorixas', 'KHRXAS', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Kunene';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Luderitz', 'LUDRTZ', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Karas';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Nkurenkuru', 'NKRNRU', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Kavango West';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Okahao', 'OKAHAO', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Omusati';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Okakarara', 'OKKRRA', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Otjozondjupa';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Omuthiya', 'OMTHYA', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Oshikoto';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Ondangwa', 'ONDNWA', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Oshana';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Ongwediva', 'ONGWVA', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Oshana';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Oniipa', 'ONIIPA', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Oshikoto';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Opuwo', 'OPUWOX', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Kunene';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Oranjemund', 'ORNJND', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Karas';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Oshakati', 'OSHKTI', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Oshana';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Oshikuku', 'OSHKKU', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Omusati';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Otavi', 'OTAVIX', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Otjozondjupa';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Outapi', 'OUTAPI', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Omusati';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Rehoboth', 'REHBTH', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Hardap';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Ruacana', 'RUACNA', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Omusati';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Rundu', 'RUNDUX', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Kavango East';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Usakos', 'USAKOS', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Town Council' AND region.value = 'Erongo';

--VILLAGE COUNCIL:

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Aroab', 'AROABX', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Karas';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Berseba', 'BERSBA', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Karas';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Bethanie', 'BETHIE', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Karas';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Bukalo', 'BUKALO', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Zambezi';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Divundu', 'DIVNDU', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Kavango East';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Gibeon', 'GIBEON', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Hardap';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Gochas', 'GOCHAS', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Hardap';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Kalkrand', 'KALKND', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Hardap';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Kamanjab', 'KAMNAB', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Kunene';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Koës', 'KOESXX', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Karas';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Leonardville', 'LENRLE', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Omaheke';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Luhonono', 'LUHNNO', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Zambezi';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Maltahöhe', 'MALTHE', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Hardap';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Okongo', 'OKONGO', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Ohangwena';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Otjinene', 'OTJNNE', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Omaheke';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Stampriet', 'STMPET', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Hardap';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Tsandi', 'TSANDI', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Omusati';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Tses', 'TSESXX', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Karas';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Witvlei', 'WITVEI', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Village Council' AND region.value = 'Omaheke';

--REGIONAL COUNCIL:

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Erongo', 'ERONGO', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Regional Council' AND region.value = 'Erongo';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Hardap', 'HARDAP', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Regional Council' AND region.value = 'Hardap';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Karas', 'KARASX', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Regional Council' AND region.value = 'Karas';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Kavango East', 'KAVEST', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Regional Council' AND region.value = 'Kavango East';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Kavango West', 'KAVWST', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Regional Council' AND region.value = 'Kavango West';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Khomas', 'KHOMAS', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Regional Council' AND region.value = 'Khomas';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Kunene', 'KUNENE', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Regional Council' AND region.value = 'Kunene';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Ohangwena', 'OHNGNA', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Regional Council' AND region.value = 'Ohangwena';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Omaheke', 'OMAHKE', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Regional Council' AND region.value = 'Omaheke';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Omusati', 'OMUSTI', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Regional Council' AND region.value = 'Omusati';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Oshana', 'OSHANA', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Regional Council' AND region.value = 'Oshana';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Oshikoto', 'OSHKTO', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Regional Council' AND region.value = 'Oshikoto';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Otjozondjupa', 'OTZNPA', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Regional Council' AND region.value = 'Otjozondjupa';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region)
    SELECT 'Zambezi', 'ZAMBZI', ra.id, region.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region
    WHERE ra.value = 'Regional Council' AND region.value = 'Zambezi';

-- ----------------------------
-- Records of cb_relevant_auth_reg_division
-- ----------------------------
/* This SQL script populates the link table for relevant authority and registration division lookup table
and should be run only after running the configuration wizard and populating the relevant authority table */

-- Municipality

INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'GOBBIS' AND regdiv.value = 'L';

INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'GRTFIN' AND regdiv.value = 'B';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'HENTAY' AND regdiv.value = 'G';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KETMOP' AND regdiv.value = 'T';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'MARNAL' AND regdiv.value = 'R';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OKHNJA' AND regdiv.value = 'J';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OMARRU' AND regdiv.value = 'C';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OTJWGO' AND regdiv.value = 'D';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OUTJOX' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'SWKPND' AND regdiv.value = 'G';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'TSUMEB' AND regdiv.value = 'B';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'WALVAY' AND regdiv.value = 'F';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'WINDEK' AND regdiv.value = 'K';

	-- Town Council

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'ARNDIS' AND regdiv.value = 'G';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'ARANOS' AND regdiv.value = 'R';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'EENHNA' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'HELNDI' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KARSRG' AND regdiv.value = 'V';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KARBIB' AND regdiv.value = 'H';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KATMLO' AND regdiv.value = 'B';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KHRXAS' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'LUDRTZ' AND regdiv.value = 'N';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'NKRNRU' AND regdiv.value = 'B';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OKAHAO' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OKKRRA' AND regdiv.value = 'D';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OMTHYA' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'ONDNWA' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'ONGWVA' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'ONIIPA' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OPUWOX' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'ORNJND' AND regdiv.value = 'N';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OSHKTI' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OSHKKU' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OTAVIX' AND regdiv.value = 'B';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OUTAPI' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'REHBTH' AND regdiv.value = 'M';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'RUACNA' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'RUNDUX' AND regdiv.value = 'B';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'USAKOS' AND regdiv.value = 'H';

-- Village Council

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'AROABX' AND regdiv.value = 'T';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'BERSBA' AND regdiv.value = 'T';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'BUKALO' AND regdiv.value = 'B';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'DIVNDU' AND regdiv.value = 'B';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'GIBEON' AND regdiv.value = 'R';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'GOCHAS' AND regdiv.value = 'R';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KALKND' AND regdiv.value = 'M';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KAMNAB' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KOESXX' AND regdiv.value = 'T';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'LENRLE' AND regdiv.value = 'L';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'LUHNNO' AND regdiv.value = 'L';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'MALTHE' AND regdiv.value = 'P';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OKONGO' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OTJNNE' AND regdiv.value = 'L';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'STMPET' AND regdiv.value = 'R';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'TSANDI' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'TSESXX' AND regdiv.value = 'T';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'MWITVEI' AND regdiv.value = 'L';

	-- Regional Council

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'ERONGO' AND regdiv.value = 'C';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'ERONGO' AND regdiv.value = 'F';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'ERONGO' AND regdiv.value = 'G';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'ERONGO' AND regdiv.value = 'H';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'ERONGO' AND regdiv.value = 'K';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'HARDAP' AND regdiv.value = 'L';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'HARDAP' AND regdiv.value = 'M';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'HARDAP' AND regdiv.value = 'N';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'HARDAP' AND regdiv.value = 'P';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'HARDAP' AND regdiv.value = 'R';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'HARDAP' AND regdiv.value = 'S';

INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'HARDAP' AND regdiv.value = 'T';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KARASX' AND regdiv.value = 'R';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KARASX' AND regdiv.value = 'N';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KARASX' AND regdiv.value = 'S';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KARASX' AND regdiv.value = 'T';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KARASX' AND regdiv.value = 'V';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KAVEST' AND regdiv.value = 'B';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KAVWST' AND regdiv.value = 'B';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KHOMAS' AND regdiv.value = 'G';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KHOMAS' AND regdiv.value = 'J';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KHOMAS' AND regdiv.value = 'K';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KHOMAS' AND regdiv.value = 'L';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KHOMAS' AND regdiv.value = 'M';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KHOMAS' AND regdiv.value = 'N';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'KUNENE' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OHNGNA' AND regdiv.value = 'A';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OHNGNA' AND regdiv.value = 'B';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OMAHKE' AND regdiv.value = 'K';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OMAHKE' AND regdiv.value = 'L';


	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OMUSTI' AND regdiv.value = 'A';


	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OSHANA' AND regdiv.value = 'A';


	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OSHKTO' AND regdiv.value = 'A';


	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OSHKTO' AND regdiv.value = 'B';


	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OTZNPA' AND regdiv.value = 'A';


	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OTZNPA' AND regdiv.value = 'B';


	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OTZNPA' AND regdiv.value = 'C';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OTZNPA' AND regdiv.value = 'D';


	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OTZNPA' AND regdiv.value = 'H';


	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OTZNPA' AND regdiv.value = 'J';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OTZNPA' AND regdiv.value = 'K';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'OTZNPA' AND regdiv.value = 'L';

	INSERT INTO cb_relevant_auth_reg_division (relv_auth_id, reg_division_id)
    SELECT ra.id, regdiv.id
    FROM cb_relevant_authority ra, cb_check_lht_reg_division regdiv
	WHERE ra.au_code = 'ZAMBZI' AND regdiv.value = 'B';
