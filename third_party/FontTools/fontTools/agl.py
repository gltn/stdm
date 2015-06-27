# The table below is taken from
# http://www.adobe.com/devnet/opentype/archives/aglfn.txt

_aglText = """\
# ###################################################################################
# Copyright (c) 2003,2005,2006,2007 Adobe Systems Incorporated
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this documentation file to use, copy, publish, distribute,
# sublicense, and/or sell copies of the documentation, and to permit
# others to do the same, provided that:
# - No modification, editing or other alteration of this document is
# allowed; and
# - The above copyright notice and this permission notice shall be
# included in all copies of the documentation.
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this documentation file, to create their own derivative works
# from the content of this document to use, copy, publish, distribute,
# sublicense, and/or sell the derivative works, and to permit others to do
# the same, provided that the derived work is not represented as being a
# copy or version of this document.
# 
# Adobe shall not be liable to any party for any loss of revenue or profit
# or for indirect, incidental, special, consequential, or other similar
# damages, whether based on tort (including without limitation negligence
# or strict liability), contract or other legal or equitable grounds even
# if Adobe has been advised or had reason to know of the possibility of
# such damages. The Adobe materials are provided on an "AS IS" basis.
# Adobe specifically disclaims all express, statutory, or implied
# warranties relating to the Adobe materials, including but not limited to
# those concerning merchantability or fitness for a particular purpose or
# non-infringement of any third party rights regarding the Adobe
# materials.
# ###################################################################################
# Name:          Adobe Glyph List For New Fonts
# Table version: 1.6
# Date:          30 Januaury 2006
#
# Description:
#
#   The Adobe Glyph List For New Fonts (AGLFN) is meant to provide a list of 
#   base glyph names which are compatible with the AGL specification at
#   http://partners.adobe.com/asn/developer/type/unicodegn.html.
#   and which can be used as described in section 6 of that document.
#
#   This list comprises the set of glyph names from the AGLv2,0 which map
#   to via the AGL rules to the semanticly correct Unicode value. For
#   example, Asmall is omitted as the AGL maps this to the Unicode
#   Private Use Area value F761, rather than to the Unicode value for the
#   character "A". "ffi" is also omitted, as the AGL maps this to the
#   Alphabetic Presentation Forms Area value FB03, rather than
#   decomposing it to the three-value Unicode sequence 0066,0066,0069.
#    See section 7.1 of the Unicode Standard 4.0 on this issue.
#   "arrowvertex" is omitted becuase this now has a real Unicode
#   character value, and the AGL is now incorrect in mapping this to the 
#   Private Use Area value  F8E6.
#
#  If you do not find an appropriate name for your glyph in this list,
#  then please refer to section 6 of the document:
#   http://partners.adobe.com/asn/developer/typeforum/unicodegn.html.
#
#	The Unicode values and names are given for convenience.
#
# Format: Semicolon-delimited fields:
#
#   (1) Standard UV or CUS UV. (4 uppercase hexadecimal digits)
#
#   (2) Glyph name. (upper- and lowercase letters, digits)
#
#   (3) Character names: Unicode character names for standard UVs, and
#       descriptive names for CUS UVs. (uppercase letters, hyphen, space)
#
#   The entries are sorted by glyph name in increasing ASCII order; entries
#   with the same glyph name are sorted in decreasing priority order.
#
#   Lines starting with "#" are comments; blank lines should be ignored.
#
#   1.6  [30 January 2006]
#	- Completed work intended in 1.5
#
#   1.5  [23 November 2005]
#      - removed duplicated block at end of file
#      - changed mappings:
#            2206;Delta;INCREMENT changed to 0394;Delta;GREEK CAPITAL LETTER DELTA
#            2126;Omega;OHM SIGN changed to 03A9;Omega;GREEK CAPITAL LETTER OMEGA
#            03BC;mu;MICRO SIGN changed to 03BC;mu;GREEK SMALL LETTER MU
#      - corrected statement above about why ffi is omitted.

#   1.4  [24 September 2003]  Changed version to 1.4, to avoid confusion 
#		with the AGL 1.3
#			fixed spelling errors in the header
#			fully removed arrowvertex, as it is mapped only to a PUA Unicode value in some fonts.
#
#   1.1  [17 April 2003]  Renamed [Tt]cedilla back to [Tt]commaaccent:
#
#   1.0  [31 Jan 2003]  Original version. Derived from the AGLv1.2 by:
#	-  removing the PUA area codes
#	- removing duplicate Unicode mappings, and 
#	- renaming tcommaaccent to tcedilla and Tcommaaccent to Tcedilla 
#
0041;A;LATIN CAPITAL LETTER A
00C6;AE;LATIN CAPITAL LETTER AE
01FC;AEacute;LATIN CAPITAL LETTER AE WITH ACUTE
00C1;Aacute;LATIN CAPITAL LETTER A WITH ACUTE
0102;Abreve;LATIN CAPITAL LETTER A WITH BREVE
00C2;Acircumflex;LATIN CAPITAL LETTER A WITH CIRCUMFLEX
00C4;Adieresis;LATIN CAPITAL LETTER A WITH DIAERESIS
00C0;Agrave;LATIN CAPITAL LETTER A WITH GRAVE
0391;Alpha;GREEK CAPITAL LETTER ALPHA
0386;Alphatonos;GREEK CAPITAL LETTER ALPHA WITH TONOS
0100;Amacron;LATIN CAPITAL LETTER A WITH MACRON
0104;Aogonek;LATIN CAPITAL LETTER A WITH OGONEK
00C5;Aring;LATIN CAPITAL LETTER A WITH RING ABOVE
01FA;Aringacute;LATIN CAPITAL LETTER A WITH RING ABOVE AND ACUTE
00C3;Atilde;LATIN CAPITAL LETTER A WITH TILDE
0042;B;LATIN CAPITAL LETTER B
0392;Beta;GREEK CAPITAL LETTER BETA
0043;C;LATIN CAPITAL LETTER C
0106;Cacute;LATIN CAPITAL LETTER C WITH ACUTE
010C;Ccaron;LATIN CAPITAL LETTER C WITH CARON
00C7;Ccedilla;LATIN CAPITAL LETTER C WITH CEDILLA
0108;Ccircumflex;LATIN CAPITAL LETTER C WITH CIRCUMFLEX
010A;Cdotaccent;LATIN CAPITAL LETTER C WITH DOT ABOVE
03A7;Chi;GREEK CAPITAL LETTER CHI
0044;D;LATIN CAPITAL LETTER D
010E;Dcaron;LATIN CAPITAL LETTER D WITH CARON
0110;Dcroat;LATIN CAPITAL LETTER D WITH STROKE
0394;Delta;GREEK CAPITAL LETTER DELTA
0045;E;LATIN CAPITAL LETTER E
00C9;Eacute;LATIN CAPITAL LETTER E WITH ACUTE
0114;Ebreve;LATIN CAPITAL LETTER E WITH BREVE
011A;Ecaron;LATIN CAPITAL LETTER E WITH CARON
00CA;Ecircumflex;LATIN CAPITAL LETTER E WITH CIRCUMFLEX
00CB;Edieresis;LATIN CAPITAL LETTER E WITH DIAERESIS
0116;Edotaccent;LATIN CAPITAL LETTER E WITH DOT ABOVE
00C8;Egrave;LATIN CAPITAL LETTER E WITH GRAVE
0112;Emacron;LATIN CAPITAL LETTER E WITH MACRON
014A;Eng;LATIN CAPITAL LETTER ENG
0118;Eogonek;LATIN CAPITAL LETTER E WITH OGONEK
0395;Epsilon;GREEK CAPITAL LETTER EPSILON
0388;Epsilontonos;GREEK CAPITAL LETTER EPSILON WITH TONOS
0397;Eta;GREEK CAPITAL LETTER ETA
0389;Etatonos;GREEK CAPITAL LETTER ETA WITH TONOS
00D0;Eth;LATIN CAPITAL LETTER ETH
20AC;Euro;EURO SIGN
0046;F;LATIN CAPITAL LETTER F
0047;G;LATIN CAPITAL LETTER G
0393;Gamma;GREEK CAPITAL LETTER GAMMA
011E;Gbreve;LATIN CAPITAL LETTER G WITH BREVE
01E6;Gcaron;LATIN CAPITAL LETTER G WITH CARON
011C;Gcircumflex;LATIN CAPITAL LETTER G WITH CIRCUMFLEX
0122;Gcommaaccent;LATIN CAPITAL LETTER G WITH CEDILLA
0120;Gdotaccent;LATIN CAPITAL LETTER G WITH DOT ABOVE
0048;H;LATIN CAPITAL LETTER H
25CF;H18533;BLACK CIRCLE
25AA;H18543;BLACK SMALL SQUARE
25AB;H18551;WHITE SMALL SQUARE
25A1;H22073;WHITE SQUARE
0126;Hbar;LATIN CAPITAL LETTER H WITH STROKE
0124;Hcircumflex;LATIN CAPITAL LETTER H WITH CIRCUMFLEX
0049;I;LATIN CAPITAL LETTER I
0132;IJ;LATIN CAPITAL LIGATURE IJ
00CD;Iacute;LATIN CAPITAL LETTER I WITH ACUTE
012C;Ibreve;LATIN CAPITAL LETTER I WITH BREVE
00CE;Icircumflex;LATIN CAPITAL LETTER I WITH CIRCUMFLEX
00CF;Idieresis;LATIN CAPITAL LETTER I WITH DIAERESIS
0130;Idotaccent;LATIN CAPITAL LETTER I WITH DOT ABOVE
2111;Ifraktur;BLACK-LETTER CAPITAL I
00CC;Igrave;LATIN CAPITAL LETTER I WITH GRAVE
012A;Imacron;LATIN CAPITAL LETTER I WITH MACRON
012E;Iogonek;LATIN CAPITAL LETTER I WITH OGONEK
0399;Iota;GREEK CAPITAL LETTER IOTA
03AA;Iotadieresis;GREEK CAPITAL LETTER IOTA WITH DIALYTIKA
038A;Iotatonos;GREEK CAPITAL LETTER IOTA WITH TONOS
0128;Itilde;LATIN CAPITAL LETTER I WITH TILDE
004A;J;LATIN CAPITAL LETTER J
0134;Jcircumflex;LATIN CAPITAL LETTER J WITH CIRCUMFLEX
004B;K;LATIN CAPITAL LETTER K
039A;Kappa;GREEK CAPITAL LETTER KAPPA
0136;Kcommaaccent;LATIN CAPITAL LETTER K WITH CEDILLA
004C;L;LATIN CAPITAL LETTER L
0139;Lacute;LATIN CAPITAL LETTER L WITH ACUTE
039B;Lambda;GREEK CAPITAL LETTER LAMDA
013D;Lcaron;LATIN CAPITAL LETTER L WITH CARON
013B;Lcommaaccent;LATIN CAPITAL LETTER L WITH CEDILLA
013F;Ldot;LATIN CAPITAL LETTER L WITH MIDDLE DOT
0141;Lslash;LATIN CAPITAL LETTER L WITH STROKE
004D;M;LATIN CAPITAL LETTER M
039C;Mu;GREEK CAPITAL LETTER MU
004E;N;LATIN CAPITAL LETTER N
0143;Nacute;LATIN CAPITAL LETTER N WITH ACUTE
0147;Ncaron;LATIN CAPITAL LETTER N WITH CARON
0145;Ncommaaccent;LATIN CAPITAL LETTER N WITH CEDILLA
00D1;Ntilde;LATIN CAPITAL LETTER N WITH TILDE
039D;Nu;GREEK CAPITAL LETTER NU
004F;O;LATIN CAPITAL LETTER O
0152;OE;LATIN CAPITAL LIGATURE OE
00D3;Oacute;LATIN CAPITAL LETTER O WITH ACUTE
014E;Obreve;LATIN CAPITAL LETTER O WITH BREVE
00D4;Ocircumflex;LATIN CAPITAL LETTER O WITH CIRCUMFLEX
00D6;Odieresis;LATIN CAPITAL LETTER O WITH DIAERESIS
00D2;Ograve;LATIN CAPITAL LETTER O WITH GRAVE
01A0;Ohorn;LATIN CAPITAL LETTER O WITH HORN
0150;Ohungarumlaut;LATIN CAPITAL LETTER O WITH DOUBLE ACUTE
014C;Omacron;LATIN CAPITAL LETTER O WITH MACRON
03A9;Omega;GREEK CAPITAL LETTER OMEGA
038F;Omegatonos;GREEK CAPITAL LETTER OMEGA WITH TONOS
039F;Omicron;GREEK CAPITAL LETTER OMICRON
038C;Omicrontonos;GREEK CAPITAL LETTER OMICRON WITH TONOS
00D8;Oslash;LATIN CAPITAL LETTER O WITH STROKE
01FE;Oslashacute;LATIN CAPITAL LETTER O WITH STROKE AND ACUTE
00D5;Otilde;LATIN CAPITAL LETTER O WITH TILDE
0050;P;LATIN CAPITAL LETTER P
03A6;Phi;GREEK CAPITAL LETTER PHI
03A0;Pi;GREEK CAPITAL LETTER PI
03A8;Psi;GREEK CAPITAL LETTER PSI
0051;Q;LATIN CAPITAL LETTER Q
0052;R;LATIN CAPITAL LETTER R
0154;Racute;LATIN CAPITAL LETTER R WITH ACUTE
0158;Rcaron;LATIN CAPITAL LETTER R WITH CARON
0156;Rcommaaccent;LATIN CAPITAL LETTER R WITH CEDILLA
211C;Rfraktur;BLACK-LETTER CAPITAL R
03A1;Rho;GREEK CAPITAL LETTER RHO
0053;S;LATIN CAPITAL LETTER S
250C;SF010000;BOX DRAWINGS LIGHT DOWN AND RIGHT
2514;SF020000;BOX DRAWINGS LIGHT UP AND RIGHT
2510;SF030000;BOX DRAWINGS LIGHT DOWN AND LEFT
2518;SF040000;BOX DRAWINGS LIGHT UP AND LEFT
253C;SF050000;BOX DRAWINGS LIGHT VERTICAL AND HORIZONTAL
252C;SF060000;BOX DRAWINGS LIGHT DOWN AND HORIZONTAL
2534;SF070000;BOX DRAWINGS LIGHT UP AND HORIZONTAL
251C;SF080000;BOX DRAWINGS LIGHT VERTICAL AND RIGHT
2524;SF090000;BOX DRAWINGS LIGHT VERTICAL AND LEFT
2500;SF100000;BOX DRAWINGS LIGHT HORIZONTAL
2502;SF110000;BOX DRAWINGS LIGHT VERTICAL
2561;SF190000;BOX DRAWINGS VERTICAL SINGLE AND LEFT DOUBLE
2562;SF200000;BOX DRAWINGS VERTICAL DOUBLE AND LEFT SINGLE
2556;SF210000;BOX DRAWINGS DOWN DOUBLE AND LEFT SINGLE
2555;SF220000;BOX DRAWINGS DOWN SINGLE AND LEFT DOUBLE
2563;SF230000;BOX DRAWINGS DOUBLE VERTICAL AND LEFT
2551;SF240000;BOX DRAWINGS DOUBLE VERTICAL
2557;SF250000;BOX DRAWINGS DOUBLE DOWN AND LEFT
255D;SF260000;BOX DRAWINGS DOUBLE UP AND LEFT
255C;SF270000;BOX DRAWINGS UP DOUBLE AND LEFT SINGLE
255B;SF280000;BOX DRAWINGS UP SINGLE AND LEFT DOUBLE
255E;SF360000;BOX DRAWINGS VERTICAL SINGLE AND RIGHT DOUBLE
255F;SF370000;BOX DRAWINGS VERTICAL DOUBLE AND RIGHT SINGLE
255A;SF380000;BOX DRAWINGS DOUBLE UP AND RIGHT
2554;SF390000;BOX DRAWINGS DOUBLE DOWN AND RIGHT
2569;SF400000;BOX DRAWINGS DOUBLE UP AND HORIZONTAL
2566;SF410000;BOX DRAWINGS DOUBLE DOWN AND HORIZONTAL
2560;SF420000;BOX DRAWINGS DOUBLE VERTICAL AND RIGHT
2550;SF430000;BOX DRAWINGS DOUBLE HORIZONTAL
256C;SF440000;BOX DRAWINGS DOUBLE VERTICAL AND HORIZONTAL
2567;SF450000;BOX DRAWINGS UP SINGLE AND HORIZONTAL DOUBLE
2568;SF460000;BOX DRAWINGS UP DOUBLE AND HORIZONTAL SINGLE
2564;SF470000;BOX DRAWINGS DOWN SINGLE AND HORIZONTAL DOUBLE
2565;SF480000;BOX DRAWINGS DOWN DOUBLE AND HORIZONTAL SINGLE
2559;SF490000;BOX DRAWINGS UP DOUBLE AND RIGHT SINGLE
2558;SF500000;BOX DRAWINGS UP SINGLE AND RIGHT DOUBLE
2552;SF510000;BOX DRAWINGS DOWN SINGLE AND RIGHT DOUBLE
2553;SF520000;BOX DRAWINGS DOWN DOUBLE AND RIGHT SINGLE
256B;SF530000;BOX DRAWINGS VERTICAL DOUBLE AND HORIZONTAL SINGLE
256A;SF540000;BOX DRAWINGS VERTICAL SINGLE AND HORIZONTAL DOUBLE
015A;Sacute;LATIN CAPITAL LETTER S WITH ACUTE
0160;Scaron;LATIN CAPITAL LETTER S WITH CARON
015E;Scedilla;LATIN CAPITAL LETTER S WITH CEDILLA
015C;Scircumflex;LATIN CAPITAL LETTER S WITH CIRCUMFLEX
0218;Scommaaccent;LATIN CAPITAL LETTER S WITH COMMA BELOW
03A3;Sigma;GREEK CAPITAL LETTER SIGMA
0054;T;LATIN CAPITAL LETTER T
03A4;Tau;GREEK CAPITAL LETTER TAU
0166;Tbar;LATIN CAPITAL LETTER T WITH STROKE
0164;Tcaron;LATIN CAPITAL LETTER T WITH CARON
0162;Tcommaaccent;LATIN CAPITAL LETTER T WITH CEDILLA
0398;Theta;GREEK CAPITAL LETTER THETA
00DE;Thorn;LATIN CAPITAL LETTER THORN
0055;U;LATIN CAPITAL LETTER U
00DA;Uacute;LATIN CAPITAL LETTER U WITH ACUTE
016C;Ubreve;LATIN CAPITAL LETTER U WITH BREVE
00DB;Ucircumflex;LATIN CAPITAL LETTER U WITH CIRCUMFLEX
00DC;Udieresis;LATIN CAPITAL LETTER U WITH DIAERESIS
00D9;Ugrave;LATIN CAPITAL LETTER U WITH GRAVE
01AF;Uhorn;LATIN CAPITAL LETTER U WITH HORN
0170;Uhungarumlaut;LATIN CAPITAL LETTER U WITH DOUBLE ACUTE
016A;Umacron;LATIN CAPITAL LETTER U WITH MACRON
0172;Uogonek;LATIN CAPITAL LETTER U WITH OGONEK
03A5;Upsilon;GREEK CAPITAL LETTER UPSILON
03D2;Upsilon1;GREEK UPSILON WITH HOOK SYMBOL
03AB;Upsilondieresis;GREEK CAPITAL LETTER UPSILON WITH DIALYTIKA
038E;Upsilontonos;GREEK CAPITAL LETTER UPSILON WITH TONOS
016E;Uring;LATIN CAPITAL LETTER U WITH RING ABOVE
0168;Utilde;LATIN CAPITAL LETTER U WITH TILDE
0056;V;LATIN CAPITAL LETTER V
0057;W;LATIN CAPITAL LETTER W
1E82;Wacute;LATIN CAPITAL LETTER W WITH ACUTE
0174;Wcircumflex;LATIN CAPITAL LETTER W WITH CIRCUMFLEX
1E84;Wdieresis;LATIN CAPITAL LETTER W WITH DIAERESIS
1E80;Wgrave;LATIN CAPITAL LETTER W WITH GRAVE
0058;X;LATIN CAPITAL LETTER X
039E;Xi;GREEK CAPITAL LETTER XI
0059;Y;LATIN CAPITAL LETTER Y
00DD;Yacute;LATIN CAPITAL LETTER Y WITH ACUTE
0176;Ycircumflex;LATIN CAPITAL LETTER Y WITH CIRCUMFLEX
0178;Ydieresis;LATIN CAPITAL LETTER Y WITH DIAERESIS
1EF2;Ygrave;LATIN CAPITAL LETTER Y WITH GRAVE
005A;Z;LATIN CAPITAL LETTER Z
0179;Zacute;LATIN CAPITAL LETTER Z WITH ACUTE
017D;Zcaron;LATIN CAPITAL LETTER Z WITH CARON
017B;Zdotaccent;LATIN CAPITAL LETTER Z WITH DOT ABOVE
0396;Zeta;GREEK CAPITAL LETTER ZETA
0061;a;LATIN SMALL LETTER A
00E1;aacute;LATIN SMALL LETTER A WITH ACUTE
0103;abreve;LATIN SMALL LETTER A WITH BREVE
00E2;acircumflex;LATIN SMALL LETTER A WITH CIRCUMFLEX
00B4;acute;ACUTE ACCENT
0301;acutecomb;COMBINING ACUTE ACCENT
00E4;adieresis;LATIN SMALL LETTER A WITH DIAERESIS
00E6;ae;LATIN SMALL LETTER AE
01FD;aeacute;LATIN SMALL LETTER AE WITH ACUTE
2015;afii00208;HORIZONTAL BAR
0410;afii10017;CYRILLIC CAPITAL LETTER A
0411;afii10018;CYRILLIC CAPITAL LETTER BE
0412;afii10019;CYRILLIC CAPITAL LETTER VE
0413;afii10020;CYRILLIC CAPITAL LETTER GHE
0414;afii10021;CYRILLIC CAPITAL LETTER DE
0415;afii10022;CYRILLIC CAPITAL LETTER IE
0401;afii10023;CYRILLIC CAPITAL LETTER IO
0416;afii10024;CYRILLIC CAPITAL LETTER ZHE
0417;afii10025;CYRILLIC CAPITAL LETTER ZE
0418;afii10026;CYRILLIC CAPITAL LETTER I
0419;afii10027;CYRILLIC CAPITAL LETTER SHORT I
041A;afii10028;CYRILLIC CAPITAL LETTER KA
041B;afii10029;CYRILLIC CAPITAL LETTER EL
041C;afii10030;CYRILLIC CAPITAL LETTER EM
041D;afii10031;CYRILLIC CAPITAL LETTER EN
041E;afii10032;CYRILLIC CAPITAL LETTER O
041F;afii10033;CYRILLIC CAPITAL LETTER PE
0420;afii10034;CYRILLIC CAPITAL LETTER ER
0421;afii10035;CYRILLIC CAPITAL LETTER ES
0422;afii10036;CYRILLIC CAPITAL LETTER TE
0423;afii10037;CYRILLIC CAPITAL LETTER U
0424;afii10038;CYRILLIC CAPITAL LETTER EF
0425;afii10039;CYRILLIC CAPITAL LETTER HA
0426;afii10040;CYRILLIC CAPITAL LETTER TSE
0427;afii10041;CYRILLIC CAPITAL LETTER CHE
0428;afii10042;CYRILLIC CAPITAL LETTER SHA
0429;afii10043;CYRILLIC CAPITAL LETTER SHCHA
042A;afii10044;CYRILLIC CAPITAL LETTER HARD SIGN
042B;afii10045;CYRILLIC CAPITAL LETTER YERU
042C;afii10046;CYRILLIC CAPITAL LETTER SOFT SIGN
042D;afii10047;CYRILLIC CAPITAL LETTER E
042E;afii10048;CYRILLIC CAPITAL LETTER YU
042F;afii10049;CYRILLIC CAPITAL LETTER YA
0490;afii10050;CYRILLIC CAPITAL LETTER GHE WITH UPTURN
0402;afii10051;CYRILLIC CAPITAL LETTER DJE
0403;afii10052;CYRILLIC CAPITAL LETTER GJE
0404;afii10053;CYRILLIC CAPITAL LETTER UKRAINIAN IE
0405;afii10054;CYRILLIC CAPITAL LETTER DZE
0406;afii10055;CYRILLIC CAPITAL LETTER BYELORUSSIAN-UKRAINIAN I
0407;afii10056;CYRILLIC CAPITAL LETTER YI
0408;afii10057;CYRILLIC CAPITAL LETTER JE
0409;afii10058;CYRILLIC CAPITAL LETTER LJE
040A;afii10059;CYRILLIC CAPITAL LETTER NJE
040B;afii10060;CYRILLIC CAPITAL LETTER TSHE
040C;afii10061;CYRILLIC CAPITAL LETTER KJE
040E;afii10062;CYRILLIC CAPITAL LETTER SHORT U
0430;afii10065;CYRILLIC SMALL LETTER A
0431;afii10066;CYRILLIC SMALL LETTER BE
0432;afii10067;CYRILLIC SMALL LETTER VE
0433;afii10068;CYRILLIC SMALL LETTER GHE
0434;afii10069;CYRILLIC SMALL LETTER DE
0435;afii10070;CYRILLIC SMALL LETTER IE
0451;afii10071;CYRILLIC SMALL LETTER IO
0436;afii10072;CYRILLIC SMALL LETTER ZHE
0437;afii10073;CYRILLIC SMALL LETTER ZE
0438;afii10074;CYRILLIC SMALL LETTER I
0439;afii10075;CYRILLIC SMALL LETTER SHORT I
043A;afii10076;CYRILLIC SMALL LETTER KA
043B;afii10077;CYRILLIC SMALL LETTER EL
043C;afii10078;CYRILLIC SMALL LETTER EM
043D;afii10079;CYRILLIC SMALL LETTER EN
043E;afii10080;CYRILLIC SMALL LETTER O
043F;afii10081;CYRILLIC SMALL LETTER PE
0440;afii10082;CYRILLIC SMALL LETTER ER
0441;afii10083;CYRILLIC SMALL LETTER ES
0442;afii10084;CYRILLIC SMALL LETTER TE
0443;afii10085;CYRILLIC SMALL LETTER U
0444;afii10086;CYRILLIC SMALL LETTER EF
0445;afii10087;CYRILLIC SMALL LETTER HA
0446;afii10088;CYRILLIC SMALL LETTER TSE
0447;afii10089;CYRILLIC SMALL LETTER CHE
0448;afii10090;CYRILLIC SMALL LETTER SHA
0449;afii10091;CYRILLIC SMALL LETTER SHCHA
044A;afii10092;CYRILLIC SMALL LETTER HARD SIGN
044B;afii10093;CYRILLIC SMALL LETTER YERU
044C;afii10094;CYRILLIC SMALL LETTER SOFT SIGN
044D;afii10095;CYRILLIC SMALL LETTER E
044E;afii10096;CYRILLIC SMALL LETTER YU
044F;afii10097;CYRILLIC SMALL LETTER YA
0491;afii10098;CYRILLIC SMALL LETTER GHE WITH UPTURN
0452;afii10099;CYRILLIC SMALL LETTER DJE
0453;afii10100;CYRILLIC SMALL LETTER GJE
0454;afii10101;CYRILLIC SMALL LETTER UKRAINIAN IE
0455;afii10102;CYRILLIC SMALL LETTER DZE
0456;afii10103;CYRILLIC SMALL LETTER BYELORUSSIAN-UKRAINIAN I
0457;afii10104;CYRILLIC SMALL LETTER YI
0458;afii10105;CYRILLIC SMALL LETTER JE
0459;afii10106;CYRILLIC SMALL LETTER LJE
045A;afii10107;CYRILLIC SMALL LETTER NJE
045B;afii10108;CYRILLIC SMALL LETTER TSHE
045C;afii10109;CYRILLIC SMALL LETTER KJE
045E;afii10110;CYRILLIC SMALL LETTER SHORT U
040F;afii10145;CYRILLIC CAPITAL LETTER DZHE
0462;afii10146;CYRILLIC CAPITAL LETTER YAT
0472;afii10147;CYRILLIC CAPITAL LETTER FITA
0474;afii10148;CYRILLIC CAPITAL LETTER IZHITSA
045F;afii10193;CYRILLIC SMALL LETTER DZHE
0463;afii10194;CYRILLIC SMALL LETTER YAT
0473;afii10195;CYRILLIC SMALL LETTER FITA
0475;afii10196;CYRILLIC SMALL LETTER IZHITSA
04D9;afii10846;CYRILLIC SMALL LETTER SCHWA
200E;afii299;LEFT-TO-RIGHT MARK
200F;afii300;RIGHT-TO-LEFT MARK
200D;afii301;ZERO WIDTH JOINER
066A;afii57381;ARABIC PERCENT SIGN
060C;afii57388;ARABIC COMMA
0660;afii57392;ARABIC-INDIC DIGIT ZERO
0661;afii57393;ARABIC-INDIC DIGIT ONE
0662;afii57394;ARABIC-INDIC DIGIT TWO
0663;afii57395;ARABIC-INDIC DIGIT THREE
0664;afii57396;ARABIC-INDIC DIGIT FOUR
0665;afii57397;ARABIC-INDIC DIGIT FIVE
0666;afii57398;ARABIC-INDIC DIGIT SIX
0667;afii57399;ARABIC-INDIC DIGIT SEVEN
0668;afii57400;ARABIC-INDIC DIGIT EIGHT
0669;afii57401;ARABIC-INDIC DIGIT NINE
061B;afii57403;ARABIC SEMICOLON
061F;afii57407;ARABIC QUESTION MARK
0621;afii57409;ARABIC LETTER HAMZA
0622;afii57410;ARABIC LETTER ALEF WITH MADDA ABOVE
0623;afii57411;ARABIC LETTER ALEF WITH HAMZA ABOVE
0624;afii57412;ARABIC LETTER WAW WITH HAMZA ABOVE
0625;afii57413;ARABIC LETTER ALEF WITH HAMZA BELOW
0626;afii57414;ARABIC LETTER YEH WITH HAMZA ABOVE
0627;afii57415;ARABIC LETTER ALEF
0628;afii57416;ARABIC LETTER BEH
0629;afii57417;ARABIC LETTER TEH MARBUTA
062A;afii57418;ARABIC LETTER TEH
062B;afii57419;ARABIC LETTER THEH
062C;afii57420;ARABIC LETTER JEEM
062D;afii57421;ARABIC LETTER HAH
062E;afii57422;ARABIC LETTER KHAH
062F;afii57423;ARABIC LETTER DAL
0630;afii57424;ARABIC LETTER THAL
0631;afii57425;ARABIC LETTER REH
0632;afii57426;ARABIC LETTER ZAIN
0633;afii57427;ARABIC LETTER SEEN
0634;afii57428;ARABIC LETTER SHEEN
0635;afii57429;ARABIC LETTER SAD
0636;afii57430;ARABIC LETTER DAD
0637;afii57431;ARABIC LETTER TAH
0638;afii57432;ARABIC LETTER ZAH
0639;afii57433;ARABIC LETTER AIN
063A;afii57434;ARABIC LETTER GHAIN
0640;afii57440;ARABIC TATWEEL
0641;afii57441;ARABIC LETTER FEH
0642;afii57442;ARABIC LETTER QAF
0643;afii57443;ARABIC LETTER KAF
0644;afii57444;ARABIC LETTER LAM
0645;afii57445;ARABIC LETTER MEEM
0646;afii57446;ARABIC LETTER NOON
0648;afii57448;ARABIC LETTER WAW
0649;afii57449;ARABIC LETTER ALEF MAKSURA
064A;afii57450;ARABIC LETTER YEH
064B;afii57451;ARABIC FATHATAN
064C;afii57452;ARABIC DAMMATAN
064D;afii57453;ARABIC KASRATAN
064E;afii57454;ARABIC FATHA
064F;afii57455;ARABIC DAMMA
0650;afii57456;ARABIC KASRA
0651;afii57457;ARABIC SHADDA
0652;afii57458;ARABIC SUKUN
0647;afii57470;ARABIC LETTER HEH
06A4;afii57505;ARABIC LETTER VEH
067E;afii57506;ARABIC LETTER PEH
0686;afii57507;ARABIC LETTER TCHEH
0698;afii57508;ARABIC LETTER JEH
06AF;afii57509;ARABIC LETTER GAF
0679;afii57511;ARABIC LETTER TTEH
0688;afii57512;ARABIC LETTER DDAL
0691;afii57513;ARABIC LETTER RREH
06BA;afii57514;ARABIC LETTER NOON GHUNNA
06D2;afii57519;ARABIC LETTER YEH BARREE
06D5;afii57534;ARABIC LETTER AE
20AA;afii57636;NEW SHEQEL SIGN
05BE;afii57645;HEBREW PUNCTUATION MAQAF
05C3;afii57658;HEBREW PUNCTUATION SOF PASUQ
05D0;afii57664;HEBREW LETTER ALEF
05D1;afii57665;HEBREW LETTER BET
05D2;afii57666;HEBREW LETTER GIMEL
05D3;afii57667;HEBREW LETTER DALET
05D4;afii57668;HEBREW LETTER HE
05D5;afii57669;HEBREW LETTER VAV
05D6;afii57670;HEBREW LETTER ZAYIN
05D7;afii57671;HEBREW LETTER HET
05D8;afii57672;HEBREW LETTER TET
05D9;afii57673;HEBREW LETTER YOD
05DA;afii57674;HEBREW LETTER FINAL KAF
05DB;afii57675;HEBREW LETTER KAF
05DC;afii57676;HEBREW LETTER LAMED
05DD;afii57677;HEBREW LETTER FINAL MEM
05DE;afii57678;HEBREW LETTER MEM
05DF;afii57679;HEBREW LETTER FINAL NUN
05E0;afii57680;HEBREW LETTER NUN
05E1;afii57681;HEBREW LETTER SAMEKH
05E2;afii57682;HEBREW LETTER AYIN
05E3;afii57683;HEBREW LETTER FINAL PE
05E4;afii57684;HEBREW LETTER PE
05E5;afii57685;HEBREW LETTER FINAL TSADI
05E6;afii57686;HEBREW LETTER TSADI
05E7;afii57687;HEBREW LETTER QOF
05E8;afii57688;HEBREW LETTER RESH
05E9;afii57689;HEBREW LETTER SHIN
05EA;afii57690;HEBREW LETTER TAV
05F0;afii57716;HEBREW LIGATURE YIDDISH DOUBLE VAV
05F1;afii57717;HEBREW LIGATURE YIDDISH VAV YOD
05F2;afii57718;HEBREW LIGATURE YIDDISH DOUBLE YOD
05B4;afii57793;HEBREW POINT HIRIQ
05B5;afii57794;HEBREW POINT TSERE
05B6;afii57795;HEBREW POINT SEGOL
05BB;afii57796;HEBREW POINT QUBUTS
05B8;afii57797;HEBREW POINT QAMATS
05B7;afii57798;HEBREW POINT PATAH
05B0;afii57799;HEBREW POINT SHEVA
05B2;afii57800;HEBREW POINT HATAF PATAH
05B1;afii57801;HEBREW POINT HATAF SEGOL
05B3;afii57802;HEBREW POINT HATAF QAMATS
05C2;afii57803;HEBREW POINT SIN DOT
05C1;afii57804;HEBREW POINT SHIN DOT
05B9;afii57806;HEBREW POINT HOLAM
05BC;afii57807;HEBREW POINT DAGESH OR MAPIQ
05BD;afii57839;HEBREW POINT METEG
05BF;afii57841;HEBREW POINT RAFE
05C0;afii57842;HEBREW PUNCTUATION PASEQ
02BC;afii57929;MODIFIER LETTER APOSTROPHE
2105;afii61248;CARE OF
2113;afii61289;SCRIPT SMALL L
2116;afii61352;NUMERO SIGN
202C;afii61573;POP DIRECTIONAL FORMATTING
202D;afii61574;LEFT-TO-RIGHT OVERRIDE
202E;afii61575;RIGHT-TO-LEFT OVERRIDE
200C;afii61664;ZERO WIDTH NON-JOINER
066D;afii63167;ARABIC FIVE POINTED STAR
02BD;afii64937;MODIFIER LETTER REVERSED COMMA
00E0;agrave;LATIN SMALL LETTER A WITH GRAVE
2135;aleph;ALEF SYMBOL
03B1;alpha;GREEK SMALL LETTER ALPHA
03AC;alphatonos;GREEK SMALL LETTER ALPHA WITH TONOS
0101;amacron;LATIN SMALL LETTER A WITH MACRON
0026;ampersand;AMPERSAND
2220;angle;ANGLE
2329;angleleft;LEFT-POINTING ANGLE BRACKET
232A;angleright;RIGHT-POINTING ANGLE BRACKET
0387;anoteleia;GREEK ANO TELEIA
0105;aogonek;LATIN SMALL LETTER A WITH OGONEK
2248;approxequal;ALMOST EQUAL TO
00E5;aring;LATIN SMALL LETTER A WITH RING ABOVE
01FB;aringacute;LATIN SMALL LETTER A WITH RING ABOVE AND ACUTE
2194;arrowboth;LEFT RIGHT ARROW
21D4;arrowdblboth;LEFT RIGHT DOUBLE ARROW
21D3;arrowdbldown;DOWNWARDS DOUBLE ARROW
21D0;arrowdblleft;LEFTWARDS DOUBLE ARROW
21D2;arrowdblright;RIGHTWARDS DOUBLE ARROW
21D1;arrowdblup;UPWARDS DOUBLE ARROW
2193;arrowdown;DOWNWARDS ARROW
2190;arrowleft;LEFTWARDS ARROW
2192;arrowright;RIGHTWARDS ARROW
2191;arrowup;UPWARDS ARROW
2195;arrowupdn;UP DOWN ARROW
21A8;arrowupdnbse;UP DOWN ARROW WITH BASE
005E;asciicircum;CIRCUMFLEX ACCENT
007E;asciitilde;TILDE
002A;asterisk;ASTERISK
2217;asteriskmath;ASTERISK OPERATOR
0040;at;COMMERCIAL AT
00E3;atilde;LATIN SMALL LETTER A WITH TILDE
0062;b;LATIN SMALL LETTER B
005C;backslash;REVERSE SOLIDUS
007C;bar;VERTICAL LINE
03B2;beta;GREEK SMALL LETTER BETA
2588;block;FULL BLOCK
007B;braceleft;LEFT CURLY BRACKET
007D;braceright;RIGHT CURLY BRACKET
005B;bracketleft;LEFT SQUARE BRACKET
005D;bracketright;RIGHT SQUARE BRACKET
02D8;breve;BREVE
00A6;brokenbar;BROKEN BAR
2022;bullet;BULLET
0063;c;LATIN SMALL LETTER C
0107;cacute;LATIN SMALL LETTER C WITH ACUTE
02C7;caron;CARON
21B5;carriagereturn;DOWNWARDS ARROW WITH CORNER LEFTWARDS
010D;ccaron;LATIN SMALL LETTER C WITH CARON
00E7;ccedilla;LATIN SMALL LETTER C WITH CEDILLA
0109;ccircumflex;LATIN SMALL LETTER C WITH CIRCUMFLEX
010B;cdotaccent;LATIN SMALL LETTER C WITH DOT ABOVE
00B8;cedilla;CEDILLA
00A2;cent;CENT SIGN
03C7;chi;GREEK SMALL LETTER CHI
25CB;circle;WHITE CIRCLE
2297;circlemultiply;CIRCLED TIMES
2295;circleplus;CIRCLED PLUS
02C6;circumflex;MODIFIER LETTER CIRCUMFLEX ACCENT
2663;club;BLACK CLUB SUIT
003A;colon;COLON
20A1;colonmonetary;COLON SIGN
002C;comma;COMMA
2245;congruent;APPROXIMATELY EQUAL TO
00A9;copyright;COPYRIGHT SIGN
00A4;currency;CURRENCY SIGN
0064;d;LATIN SMALL LETTER D
2020;dagger;DAGGER
2021;daggerdbl;DOUBLE DAGGER
010F;dcaron;LATIN SMALL LETTER D WITH CARON
0111;dcroat;LATIN SMALL LETTER D WITH STROKE
00B0;degree;DEGREE SIGN
03B4;delta;GREEK SMALL LETTER DELTA
2666;diamond;BLACK DIAMOND SUIT
00A8;dieresis;DIAERESIS
0385;dieresistonos;GREEK DIALYTIKA TONOS
00F7;divide;DIVISION SIGN
2593;dkshade;DARK SHADE
2584;dnblock;LOWER HALF BLOCK
0024;dollar;DOLLAR SIGN
20AB;dong;DONG SIGN
02D9;dotaccent;DOT ABOVE
0323;dotbelowcomb;COMBINING DOT BELOW
0131;dotlessi;LATIN SMALL LETTER DOTLESS I
22C5;dotmath;DOT OPERATOR
0065;e;LATIN SMALL LETTER E
00E9;eacute;LATIN SMALL LETTER E WITH ACUTE
0115;ebreve;LATIN SMALL LETTER E WITH BREVE
011B;ecaron;LATIN SMALL LETTER E WITH CARON
00EA;ecircumflex;LATIN SMALL LETTER E WITH CIRCUMFLEX
00EB;edieresis;LATIN SMALL LETTER E WITH DIAERESIS
0117;edotaccent;LATIN SMALL LETTER E WITH DOT ABOVE
00E8;egrave;LATIN SMALL LETTER E WITH GRAVE
0038;eight;DIGIT EIGHT
2208;element;ELEMENT OF
2026;ellipsis;HORIZONTAL ELLIPSIS
0113;emacron;LATIN SMALL LETTER E WITH MACRON
2014;emdash;EM DASH
2205;emptyset;EMPTY SET
2013;endash;EN DASH
014B;eng;LATIN SMALL LETTER ENG
0119;eogonek;LATIN SMALL LETTER E WITH OGONEK
03B5;epsilon;GREEK SMALL LETTER EPSILON
03AD;epsilontonos;GREEK SMALL LETTER EPSILON WITH TONOS
003D;equal;EQUALS SIGN
2261;equivalence;IDENTICAL TO
212E;estimated;ESTIMATED SYMBOL
03B7;eta;GREEK SMALL LETTER ETA
03AE;etatonos;GREEK SMALL LETTER ETA WITH TONOS
00F0;eth;LATIN SMALL LETTER ETH
0021;exclam;EXCLAMATION MARK
203C;exclamdbl;DOUBLE EXCLAMATION MARK
00A1;exclamdown;INVERTED EXCLAMATION MARK
2203;existential;THERE EXISTS
0066;f;LATIN SMALL LETTER F
2640;female;FEMALE SIGN
2012;figuredash;FIGURE DASH
25A0;filledbox;BLACK SQUARE
25AC;filledrect;BLACK RECTANGLE
0035;five;DIGIT FIVE
215D;fiveeighths;VULGAR FRACTION FIVE EIGHTHS
0192;florin;LATIN SMALL LETTER F WITH HOOK
0034;four;DIGIT FOUR
2044;fraction;FRACTION SLASH
20A3;franc;FRENCH FRANC SIGN
0067;g;LATIN SMALL LETTER G
03B3;gamma;GREEK SMALL LETTER GAMMA
011F;gbreve;LATIN SMALL LETTER G WITH BREVE
01E7;gcaron;LATIN SMALL LETTER G WITH CARON
011D;gcircumflex;LATIN SMALL LETTER G WITH CIRCUMFLEX
0123;gcommaaccent;LATIN SMALL LETTER G WITH CEDILLA
0121;gdotaccent;LATIN SMALL LETTER G WITH DOT ABOVE
00DF;germandbls;LATIN SMALL LETTER SHARP S
2207;gradient;NABLA
0060;grave;GRAVE ACCENT
0300;gravecomb;COMBINING GRAVE ACCENT
003E;greater;GREATER-THAN SIGN
2265;greaterequal;GREATER-THAN OR EQUAL TO
00AB;guillemotleft;LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
00BB;guillemotright;RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
2039;guilsinglleft;SINGLE LEFT-POINTING ANGLE QUOTATION MARK
203A;guilsinglright;SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
0068;h;LATIN SMALL LETTER H
0127;hbar;LATIN SMALL LETTER H WITH STROKE
0125;hcircumflex;LATIN SMALL LETTER H WITH CIRCUMFLEX
2665;heart;BLACK HEART SUIT
0309;hookabovecomb;COMBINING HOOK ABOVE
2302;house;HOUSE
02DD;hungarumlaut;DOUBLE ACUTE ACCENT
002D;hyphen;HYPHEN-MINUS
0069;i;LATIN SMALL LETTER I
00ED;iacute;LATIN SMALL LETTER I WITH ACUTE
012D;ibreve;LATIN SMALL LETTER I WITH BREVE
00EE;icircumflex;LATIN SMALL LETTER I WITH CIRCUMFLEX
00EF;idieresis;LATIN SMALL LETTER I WITH DIAERESIS
00EC;igrave;LATIN SMALL LETTER I WITH GRAVE
0133;ij;LATIN SMALL LIGATURE IJ
012B;imacron;LATIN SMALL LETTER I WITH MACRON
221E;infinity;INFINITY
222B;integral;INTEGRAL
2321;integralbt;BOTTOM HALF INTEGRAL
2320;integraltp;TOP HALF INTEGRAL
2229;intersection;INTERSECTION
25D8;invbullet;INVERSE BULLET
25D9;invcircle;INVERSE WHITE CIRCLE
263B;invsmileface;BLACK SMILING FACE
012F;iogonek;LATIN SMALL LETTER I WITH OGONEK
03B9;iota;GREEK SMALL LETTER IOTA
03CA;iotadieresis;GREEK SMALL LETTER IOTA WITH DIALYTIKA
0390;iotadieresistonos;GREEK SMALL LETTER IOTA WITH DIALYTIKA AND TONOS
03AF;iotatonos;GREEK SMALL LETTER IOTA WITH TONOS
0129;itilde;LATIN SMALL LETTER I WITH TILDE
006A;j;LATIN SMALL LETTER J
0135;jcircumflex;LATIN SMALL LETTER J WITH CIRCUMFLEX
006B;k;LATIN SMALL LETTER K
03BA;kappa;GREEK SMALL LETTER KAPPA
0137;kcommaaccent;LATIN SMALL LETTER K WITH CEDILLA
0138;kgreenlandic;LATIN SMALL LETTER KRA
006C;l;LATIN SMALL LETTER L
013A;lacute;LATIN SMALL LETTER L WITH ACUTE
03BB;lambda;GREEK SMALL LETTER LAMDA
013E;lcaron;LATIN SMALL LETTER L WITH CARON
013C;lcommaaccent;LATIN SMALL LETTER L WITH CEDILLA
0140;ldot;LATIN SMALL LETTER L WITH MIDDLE DOT
003C;less;LESS-THAN SIGN
2264;lessequal;LESS-THAN OR EQUAL TO
258C;lfblock;LEFT HALF BLOCK
20A4;lira;LIRA SIGN
2227;logicaland;LOGICAL AND
00AC;logicalnot;NOT SIGN
2228;logicalor;LOGICAL OR
017F;longs;LATIN SMALL LETTER LONG S
25CA;lozenge;LOZENGE
0142;lslash;LATIN SMALL LETTER L WITH STROKE
2591;ltshade;LIGHT SHADE
006D;m;LATIN SMALL LETTER M
00AF;macron;MACRON
2642;male;MALE SIGN
2212;minus;MINUS SIGN
2032;minute;PRIME
03BC;mu;GREEK SMALL LETTER MU
00D7;multiply;MULTIPLICATION SIGN
266A;musicalnote;EIGHTH NOTE
266B;musicalnotedbl;BEAMED EIGHTH NOTES
006E;n;LATIN SMALL LETTER N
0144;nacute;LATIN SMALL LETTER N WITH ACUTE
0149;napostrophe;LATIN SMALL LETTER N PRECEDED BY APOSTROPHE
0148;ncaron;LATIN SMALL LETTER N WITH CARON
0146;ncommaaccent;LATIN SMALL LETTER N WITH CEDILLA
0039;nine;DIGIT NINE
2209;notelement;NOT AN ELEMENT OF
2260;notequal;NOT EQUAL TO
2284;notsubset;NOT A SUBSET OF
00F1;ntilde;LATIN SMALL LETTER N WITH TILDE
03BD;nu;GREEK SMALL LETTER NU
0023;numbersign;NUMBER SIGN
006F;o;LATIN SMALL LETTER O
00F3;oacute;LATIN SMALL LETTER O WITH ACUTE
014F;obreve;LATIN SMALL LETTER O WITH BREVE
00F4;ocircumflex;LATIN SMALL LETTER O WITH CIRCUMFLEX
00F6;odieresis;LATIN SMALL LETTER O WITH DIAERESIS
0153;oe;LATIN SMALL LIGATURE OE
02DB;ogonek;OGONEK
00F2;ograve;LATIN SMALL LETTER O WITH GRAVE
01A1;ohorn;LATIN SMALL LETTER O WITH HORN
0151;ohungarumlaut;LATIN SMALL LETTER O WITH DOUBLE ACUTE
014D;omacron;LATIN SMALL LETTER O WITH MACRON
03C9;omega;GREEK SMALL LETTER OMEGA
03D6;omega1;GREEK PI SYMBOL
03CE;omegatonos;GREEK SMALL LETTER OMEGA WITH TONOS
03BF;omicron;GREEK SMALL LETTER OMICRON
03CC;omicrontonos;GREEK SMALL LETTER OMICRON WITH TONOS
0031;one;DIGIT ONE
2024;onedotenleader;ONE DOT LEADER
215B;oneeighth;VULGAR FRACTION ONE EIGHTH
00BD;onehalf;VULGAR FRACTION ONE HALF
00BC;onequarter;VULGAR FRACTION ONE QUARTER
2153;onethird;VULGAR FRACTION ONE THIRD
25E6;openbullet;WHITE BULLET
00AA;ordfeminine;FEMININE ORDINAL INDICATOR
00BA;ordmasculine;MASCULINE ORDINAL INDICATOR
221F;orthogonal;RIGHT ANGLE
00F8;oslash;LATIN SMALL LETTER O WITH STROKE
01FF;oslashacute;LATIN SMALL LETTER O WITH STROKE AND ACUTE
00F5;otilde;LATIN SMALL LETTER O WITH TILDE
0070;p;LATIN SMALL LETTER P
00B6;paragraph;PILCROW SIGN
0028;parenleft;LEFT PARENTHESIS
0029;parenright;RIGHT PARENTHESIS
2202;partialdiff;PARTIAL DIFFERENTIAL
0025;percent;PERCENT SIGN
002E;period;FULL STOP
00B7;periodcentered;MIDDLE DOT
22A5;perpendicular;UP TACK
2030;perthousand;PER MILLE SIGN
20A7;peseta;PESETA SIGN
03C6;phi;GREEK SMALL LETTER PHI
03D5;phi1;GREEK PHI SYMBOL
03C0;pi;GREEK SMALL LETTER PI
002B;plus;PLUS SIGN
00B1;plusminus;PLUS-MINUS SIGN
211E;prescription;PRESCRIPTION TAKE
220F;product;N-ARY PRODUCT
2282;propersubset;SUBSET OF
2283;propersuperset;SUPERSET OF
221D;proportional;PROPORTIONAL TO
03C8;psi;GREEK SMALL LETTER PSI
0071;q;LATIN SMALL LETTER Q
003F;question;QUESTION MARK
00BF;questiondown;INVERTED QUESTION MARK
0022;quotedbl;QUOTATION MARK
201E;quotedblbase;DOUBLE LOW-9 QUOTATION MARK
201C;quotedblleft;LEFT DOUBLE QUOTATION MARK
201D;quotedblright;RIGHT DOUBLE QUOTATION MARK
2018;quoteleft;LEFT SINGLE QUOTATION MARK
201B;quotereversed;SINGLE HIGH-REVERSED-9 QUOTATION MARK
2019;quoteright;RIGHT SINGLE QUOTATION MARK
201A;quotesinglbase;SINGLE LOW-9 QUOTATION MARK
0027;quotesingle;APOSTROPHE
0072;r;LATIN SMALL LETTER R
0155;racute;LATIN SMALL LETTER R WITH ACUTE
221A;radical;SQUARE ROOT
0159;rcaron;LATIN SMALL LETTER R WITH CARON
0157;rcommaaccent;LATIN SMALL LETTER R WITH CEDILLA
2286;reflexsubset;SUBSET OF OR EQUAL TO
2287;reflexsuperset;SUPERSET OF OR EQUAL TO
00AE;registered;REGISTERED SIGN
2310;revlogicalnot;REVERSED NOT SIGN
03C1;rho;GREEK SMALL LETTER RHO
02DA;ring;RING ABOVE
2590;rtblock;RIGHT HALF BLOCK
0073;s;LATIN SMALL LETTER S
015B;sacute;LATIN SMALL LETTER S WITH ACUTE
0161;scaron;LATIN SMALL LETTER S WITH CARON
015F;scedilla;LATIN SMALL LETTER S WITH CEDILLA
015D;scircumflex;LATIN SMALL LETTER S WITH CIRCUMFLEX
0219;scommaaccent;LATIN SMALL LETTER S WITH COMMA BELOW
2033;second;DOUBLE PRIME
00A7;section;SECTION SIGN
003B;semicolon;SEMICOLON
0037;seven;DIGIT SEVEN
215E;seveneighths;VULGAR FRACTION SEVEN EIGHTHS
2592;shade;MEDIUM SHADE
03C3;sigma;GREEK SMALL LETTER SIGMA
03C2;sigma1;GREEK SMALL LETTER FINAL SIGMA
223C;similar;TILDE OPERATOR
0036;six;DIGIT SIX
002F;slash;SOLIDUS
263A;smileface;WHITE SMILING FACE
0020;space;SPACE
2660;spade;BLACK SPADE SUIT
00A3;sterling;POUND SIGN
220B;suchthat;CONTAINS AS MEMBER
2211;summation;N-ARY SUMMATION
263C;sun;WHITE SUN WITH RAYS
0074;t;LATIN SMALL LETTER T
03C4;tau;GREEK SMALL LETTER TAU
0167;tbar;LATIN SMALL LETTER T WITH STROKE
0165;tcaron;LATIN SMALL LETTER T WITH CARON
0163;tcommaaccent;LATIN SMALL LETTER T WITH CEDILLA
2234;therefore;THEREFORE
03B8;theta;GREEK SMALL LETTER THETA
03D1;theta1;GREEK THETA SYMBOL
00FE;thorn;LATIN SMALL LETTER THORN
0033;three;DIGIT THREE
215C;threeeighths;VULGAR FRACTION THREE EIGHTHS
00BE;threequarters;VULGAR FRACTION THREE QUARTERS
02DC;tilde;SMALL TILDE
0303;tildecomb;COMBINING TILDE
0384;tonos;GREEK TONOS
2122;trademark;TRADE MARK SIGN
25BC;triagdn;BLACK DOWN-POINTING TRIANGLE
25C4;triaglf;BLACK LEFT-POINTING POINTER
25BA;triagrt;BLACK RIGHT-POINTING POINTER
25B2;triagup;BLACK UP-POINTING TRIANGLE
0032;two;DIGIT TWO
2025;twodotenleader;TWO DOT LEADER
2154;twothirds;VULGAR FRACTION TWO THIRDS
0075;u;LATIN SMALL LETTER U
00FA;uacute;LATIN SMALL LETTER U WITH ACUTE
016D;ubreve;LATIN SMALL LETTER U WITH BREVE
00FB;ucircumflex;LATIN SMALL LETTER U WITH CIRCUMFLEX
00FC;udieresis;LATIN SMALL LETTER U WITH DIAERESIS
00F9;ugrave;LATIN SMALL LETTER U WITH GRAVE
01B0;uhorn;LATIN SMALL LETTER U WITH HORN
0171;uhungarumlaut;LATIN SMALL LETTER U WITH DOUBLE ACUTE
016B;umacron;LATIN SMALL LETTER U WITH MACRON
005F;underscore;LOW LINE
2017;underscoredbl;DOUBLE LOW LINE
222A;union;UNION
2200;universal;FOR ALL
0173;uogonek;LATIN SMALL LETTER U WITH OGONEK
2580;upblock;UPPER HALF BLOCK
03C5;upsilon;GREEK SMALL LETTER UPSILON
03CB;upsilondieresis;GREEK SMALL LETTER UPSILON WITH DIALYTIKA
03B0;upsilondieresistonos;GREEK SMALL LETTER UPSILON WITH DIALYTIKA AND TONOS
03CD;upsilontonos;GREEK SMALL LETTER UPSILON WITH TONOS
016F;uring;LATIN SMALL LETTER U WITH RING ABOVE
0169;utilde;LATIN SMALL LETTER U WITH TILDE
0076;v;LATIN SMALL LETTER V
0077;w;LATIN SMALL LETTER W
1E83;wacute;LATIN SMALL LETTER W WITH ACUTE
0175;wcircumflex;LATIN SMALL LETTER W WITH CIRCUMFLEX
1E85;wdieresis;LATIN SMALL LETTER W WITH DIAERESIS
2118;weierstrass;SCRIPT CAPITAL P
1E81;wgrave;LATIN SMALL LETTER W WITH GRAVE
0078;x;LATIN SMALL LETTER X
03BE;xi;GREEK SMALL LETTER XI
0079;y;LATIN SMALL LETTER Y
00FD;yacute;LATIN SMALL LETTER Y WITH ACUTE
0177;ycircumflex;LATIN SMALL LETTER Y WITH CIRCUMFLEX
00FF;ydieresis;LATIN SMALL LETTER Y WITH DIAERESIS
00A5;yen;YEN SIGN
1EF3;ygrave;LATIN SMALL LETTER Y WITH GRAVE
007A;z;LATIN SMALL LETTER Z
017A;zacute;LATIN SMALL LETTER Z WITH ACUTE
017E;zcaron;LATIN SMALL LETTER Z WITH CARON
017C;zdotaccent;LATIN SMALL LETTER Z WITH DOT ABOVE
0030;zero;DIGIT ZERO
03B6;zeta;GREEK SMALL LETTER ZETA
"""


AGLError = "AGLError"

AGL2UV = {}
UV2AGL = {}

def _builddicts():
	import re
	
	lines = _aglText.splitlines()
	
	parseAGL_RE = re.compile("([0-9A-F]{4});([A-Za-z_0-9.]+);.*?$")
	
	for line in lines:
		if not line or line[:1] == '#':
			continue
		m = parseAGL_RE.match(line)
		if not m:
			raise AGLError, "syntax error in glyphlist.txt: %s" % repr(line[:20])
		unicode = m.group(1)
		assert len(unicode) == 4
		unicode = int(unicode, 16)
		glyphName = m.group(2)
		if AGL2UV.has_key(glyphName):
			# the above table contains identical duplicates
			assert AGL2UV[glyphName] == unicode
		else:
			AGL2UV[glyphName] = unicode
		UV2AGL[unicode] = glyphName
	
_builddicts()
