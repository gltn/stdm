/* This SQL script populated the cb_relevant_authority table and should be run only after
   running the configuration wizard */

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Gobabis', 'GOBBIS', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
	WHERE ra.value = 'Municipality Council' AND region.value = 'Omaheke' AND division.value = 'L';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Grootfontein', 'GRTFIN', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Municipality Council' AND region.value = 'Otjozondjupa' AND division.value = 'B';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Henties', 'HENTAY', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Municipality Council' AND region.value = 'Erongo' AND division.value = 'G';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Keetmanshoop', 'KETMOP', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Municipality Council' AND region.value = 'Karas' AND division.value = 'T';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Mariental', 'MARNAL', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Municipality Council' AND region.value = 'Hardap' AND division.value = 'R';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Okahandja', 'OKHNJA', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Municipality Council' AND region.value = 'Otjozondjupa' AND division.value = 'J';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Omaruru', 'OMARRU', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Municipality Council' AND region.value = 'Erongo' AND division.value = 'C';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Otjiwarongo', 'OTJWGO', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Municipality Council' AND region.value = 'Otjozondjupa' AND division.value = 'D';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Outjo', 'OUTJOX', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Municipality Council' AND region.value = 'Kunene' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Swakopmund', 'SWKPND', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Municipality Council' AND region.value = 'Erongo' AND division.value = 'G';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Tsumeb', 'TSUMEB', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Municipality Council' AND region.value = 'Oshikoto' AND division.value = 'B';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Walvis Bay', 'WALVAY', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Municipality Council' AND region.value = 'Erongo' AND division.value = 'F';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Windhoek', 'WINDEK', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Municipality Council' AND region.value = 'Khomas' AND division.value = 'K';

--TOWN COUNCIL:

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Arandis', 'ARNDIS', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Erongo' AND division.value = 'G';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Aranos', 'ARANOS', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Hardap' AND division.value = 'R';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Eenhana', 'EENHNA', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Ohangwena' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Helao Nafidi', 'HELNDI', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Ohangwena' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Karasburg', 'KARSRG', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Karas' AND division.value = 'V';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Karibib', 'KARBIB', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Erongo' AND division.value = 'H';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Katima Mulilo', 'KATMLO', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Zambezi' AND division.value = 'B';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Khorixas', 'KHRXAS', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Kunene' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Luderitz', 'LUDRTZ', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Karas' AND division.value = 'N';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Nkurenkuru', 'NKRNRU', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Kavango' AND division.value = 'B';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Okahao', 'OKAHAO', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Omusati' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Okakarara', 'OKKRRA', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Otjozondjupa' AND division.value = 'D';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Omuthiya', 'OMTHYA', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Oshikoto' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Ondangwa', 'ONDNWA', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Oshana' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Ongwediva', 'ONGWVA', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Oshana' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Oniipa', 'ONIIPA', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Oshikoto' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Opuwo', 'OPUWOX', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Kunene' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Oranjemund', 'ORNJND', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Karas' AND division.value = 'N';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Oshakati', 'OSHKTI', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Oshana' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Oshikuku', 'OSHKKU', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Omusati' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Otavi', 'OTAVIX', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Otjozondjupa' AND division.value = 'B';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Outapi', 'OUTAPI', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Omusati' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Rehoboth', 'REHBTH', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Hardap' AND division.value = 'M';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Ruacana', 'RUACNA', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Omusati' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Rundu', 'RUNDUX', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Kavango East' AND division.value = 'B';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Usakos', 'USAKOS', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Town Council' AND region.value = 'Erongo' AND division.value = 'H';

--VILLAGE COUNCIL:

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Aroab', 'AROABX', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Karas' AND division.value = 'T';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Berseba', 'BERSBA', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Karas' AND division.value = 'T';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Bethanie', 'BETHIE', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Karas' AND division.value = 'S';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Bukalo', 'BUKALO', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Zambezi' AND division.value = 'B';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Divundu', 'DIVNDU', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Kavango East' AND division.value = 'B';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Gibeon', 'GIBEON', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Hardap' AND division.value = 'R';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Gochas', 'GOCHAS', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Hardap' AND division.value = 'R';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Kalkrand', 'KALKND', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Hardap' AND division.value = 'M';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Kamanjab', 'KAMNAB', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Kunene' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Koës', 'KOESXX', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Karas' AND division.value = 'T';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Leonardville', 'LENRLE', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Omaheke' AND division.value = 'L';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Luhonono', 'LUHNNO', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Zambezi' AND division.value = 'L';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Maltahöhe', 'MALTHE', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Hardap' AND division.value = 'P';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Okongo', 'OKONGO', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Ohangwena' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Otjinene', 'OTJNNE', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Omaheke' AND division.value = 'L';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Stampriet', 'STMPET', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Hardap' AND division.value = 'R';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Tsandi', 'TSANDI', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Omusati' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Tses', 'TSESXX', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Karas' AND division.value = 'T';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Witvlei', 'WITVEI', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Village Council' AND region.value = 'Omaheke' AND division.value = 'L';

--REGIONAL COUNCIL:

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Erongo', 'ERONGO', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Regional Council' AND region.value = 'Erongo' AND division.value = 'CFGHK';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Hardap', 'HARDAP', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Regional Council' AND region.value = 'Hardap' AND division.value = 'LMNPRST';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Karas', 'KARASX', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Regional Council' AND region.value = 'Karas' AND division.value = 'NSTV';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Kavango East', 'KAVEST', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Regional Council' AND region.value = 'Kavango East' AND division.value = 'B';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Kavango West', 'KAVWST', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Regional Council' AND region.value = 'Kavango West' AND division.value = 'B';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Khomas', 'KHOMAS', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Regional Council' AND region.value = 'Khomas' AND division.value = 'GJKLMN';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Kunene', 'KUNENE', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Regional Council' AND region.value = 'Kunene' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Ohangwena', 'OHNGNA', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Regional Council' AND region.value = 'Ohangwena' AND division.value = 'AB';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Omaheke', 'OMAHKE', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Regional Council' AND region.value = 'Omaheke' AND division.value = 'KL';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Omusati', 'OMUSTI', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Regional Council' AND region.value = 'Omusati' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Oshana', 'OSHANA', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Regional Council' AND region.value = 'Oshana' AND division.value = 'A';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Oshikoto', 'OSHKTO', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Regional Council' AND region.value = 'Oshikoto' AND division.value = 'AB';

INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Otjozondjupa', 'OTZNPA', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Regional Council' AND region.value = 'Otjozondjupa' AND division.value = 'ABCDHJKL';


INSERT INTO cb_relevant_authority (name_of_relevant_authority, au_code, type_of_relevant_authority, region, registration_division)
    SELECT 'Zambezi', 'ZAMBZI', ra.id, region.id, division.id
    FROM cb_check_lht_relevant_authority ra, cb_check_lht_region region, cb_check_lht_reg_division division
    WHERE ra.value = 'Regional Council' AND region.value = 'Zambezi' AND division.value = 'B';