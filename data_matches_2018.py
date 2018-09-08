from teams_data import teams_data

def calendar():
    raw = [
            "Résultats,ASC	SCO	GDB	SMC	DFCO	EAG	LOSC	OL	OM	ASM	MHSC	FCN	OGCN	NO	PSG	SDR	SRFC	ASSE	RCSA	TFC",
            "Amiens SC,X	J18	J30	J24	J09	J38	J05	J22	J14	J16	J02	J11	J26	J28	J20	J03	J07	J31	J34	J36",
            "Angers SCO,J29	X	J17	J15	J23	J08	J04	J11	J19	J27	J13	J21	J25	J01	J36	J34	J31	J38	J09	J06",
            "Girondins de Bordeaux,J19	J35	X	J13	J21	J23	J07	J34	J31	J03	J27	J09	J11	J05	J15	J37	J29	J16	J01	J25",
            "SM Caen,J08	J32	J38	X	J34	J10	J20	J05	J21	J14	J07	J23	J02	J16	J27	J36	J12	J29	J25	J18",
            "Dijon FCO,J32	J05	J14	J04	X	J16	J10	J07	J24	J22	J20	J02	J30	J12	J18	J28	J33	J26	J36	J38",
            "EA Guingamp,J17	J26	J06	J35	J29	X	J24	J13	J33	J31	J09	J27	J15	J37	J02	J22	J18	J20	J11	J04",
            "Lille OSC,J21	J37	J36	J11	J27	J03	X	J15	J08	J29	J25	J06	J23	J34	J32	J17	J01	J09	J13	J19",
            "Olympique lyonnais,J01	J33	J12	J37	J31	J25	J35	X	J06	J18	J29	J08	J04	J10	J23	J20	J16	J14	J03	J27",
            "Olympique de Marseille,J25	J30	J18	J09	J13	J05	J22	J36	X	J20	J38	J34	J28	J32	J11	J15	J03	J27	J07	J01",
            "AS Monaco,J37	J07	J28	J30	J11	J19	J02	J26	J04	X	J15	J25	J17	J06	J13	J32	J09	J35	J21	J23",
            "Montpellier Hérault SC,J35	J28	J10	J22	J01	J30	J16	J19	J12	J24	X	J37	J06	J08	J34	J26	J14	J03	J05	J32",
            "FC Nantes,J33	J14	J26	J03	J35	J12	J30	J32	J16	J01	J18	X	J07	J24	J28	J05	J20	J22	J38	J10",
            "OGC Nice,J12	J16	J20	J33	J03	J34	J14	J24	J10	J38	J31	J36	X	J22	J08	J01	J05	J18	J27	J29",
            "Nîmes Olympique,J15	J20	J33	J31	J25	J07	J18	J38	J02	J36	J23	J17	J13	X	J04	J09	J27	J11	J29	J21",
            "Paris Saint-Germain,J10	J03	J24	J01	J37	J21	J12	J09	J29	J33	J17	J19	J35	J26	X	J07	J22	J05	J31	J14",
            "Stade de Reims,J27	J10	J08	J19	J06	J14	J31	J02	J23	J12	J04	J29	J21	J35	J38	X	J25	J33	J18	J16",
            "Stade rennais FC,J23	J02	J04	J28	J17	J36	J38	J30	J26	J34	J21	J13	J32	J19	J06	J11	X	J24	J15	J08",
            "AS Saint-Étienne,J04	J12	J32	J06	J19	J01	J28	J21	J17	J08	J36	J15	J37	J30	J25	J13	J10	X	J23	J34",
            "RC Strasbourg,J06	J24	J22	J17	J08	J32	J26	J28	J35	J10	J33	J04	J19	J14	J16	J30	J37	J02	X	J12",
            "Toulouse FC,J13	J22	J02	J26	J15	J28	J33	J17	J37	J05	J11	J31	J09	J03	J30	J24	J35	J07	J20	X"
        ]
    teams = None
    days = {}
    for i, s in enumerate(raw):
        s = s.strip()
        if not teams:
            t, r = s.split(',')
            teams = r.split("\t")
            continue
        t, r = s.split(',')
        home_team = teams[i - 1]
        for j, m in enumerate(r.split("\t")):
            if m == 'X':
                continue
            m = int(m[1:])
            if m not in days:
                days[m] = []
            days[m].append({'HomeTeam': home_team, 'AwayTeam':teams[j]})

    teams_d = teams_data()
    codes = {t['Code']: k for k, t in teams_d.items() if t['Code'] is not ''}
    matches = []
    for day in sorted(days):
        for m in days[day]:
            m['Date'] = day
            m['HomeTeam'] = codes[m['HomeTeam']]
            m['AwayTeam'] = codes[m['AwayTeam']]
            m['Played'] = False
            m['FTHG'] = None
            m['FTAG'] = None
            m['Div'] = 1
            m['FTR'] = None
            m['Prono'] = None
            m['Exact_s1'] = None
            m['Exact_s2'] = None
            matches.append(m)
    return matches

