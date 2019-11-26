import os
import sys
import glob
import json
import re
import csv
import multiprocessing

locations = pd.read_csv('university_czone.csv')
universities = pd.read_csv('universities.csv',header=None)
universities.columns = ['name','student_count']

# Read in reference schools

schools_f = open('herd_2008_unique_school.csv','rt',encoding='utf-8')
schools_c = csv.reader(schools_f)

schools_d = []
schools = []
for school in schools_c:
    schools_d.append( (set([i for i in 
                            school[9].lower().translate({ord(c): ' ' 
                            for c in '|[]_*?!@#$,.-;:"/()'}).split() 
                            if i not in ['in','at','of','for','studies','all',
                                         'campuses','main','campus','and','the',
                                         '&']]), school[9]))

schools = [i[0] for i in schools_d]
schools = schools[1:]
schools_d = schools_d[1:]

# Colloquial names found on Wikipedia

colloquial_names = {
"AECOM":["Albert Einstein College of Medicine"],
"AFA":["United States Air Force Academy"],
"Annapolis": ["U.S. Naval Academy"],
"A&M":["Texas A&M University"],
"A&M-CC":["Texas A&M University–Corpus Christi"],
"A&M-Corpus Christi":["Texas A&M University–Corpus Christi"],
"A&T":["North Carolina A&T State University"],
"Newport News":["Apprentice School"],
"APSU":["Austin Peay State University"],
"ALASU":["Alabama State University"],
"Army":["U.S. Military Academy"],
"ASU":["Alabama State University", "Albany State University", "Alcorn State University", "Angelo State University", "Appalachian State University", "Arizona State University", "Arkansas State University", "Augusta State University", "Armstrong State University"],
"AU":["Adelphi University", "Alfred University", "American University", "Anderson University", "Asbury University", "Auburn University", "Ashford University", "Arcadia University", "Augusta University"],
"AUM":["Auburn University Montgomery"],
"Bama":["University of Alabama"],
"BC":["Boston College", "Bethel College"],
"BCC":["Bronx Community College"],
"Berkeley": ["University of California, Berkeley"],
"BGSU":["Bowling Green State University"],
"BHSU":["Black Hills State University"],
"BJU":["Bob Jones University"],
"BMC":["Bryn Mawr College"],
"Bona":["St. Bonaventure University"],
"Brown":["Brown University"],
"BSC":["Birmingham-Southern College"],
"BSU":["Ball State University", "Boise State University", "Bemidji State University", "Bowie State University"],
"BU":["Baylor University", "Belmont University", "Binghamton University", "Biola University", "Boston University", "Bradley University", "Butler University"],
"BYU":["Brigham Young University"],
"CBU":["California Baptist University"],
"C of C":["College of Charleston"],
"Cal":["University of California, Berkeley"],
"Cal Poly":["California Polytechnic State University, San Luis Obispo"],
"Cal Poly Pomona":["California State Polytechnic University, Pomona"],
"Caltech":["California Institute of Technology"],
"Cal U":["California University of Pennsylvania"],
"CUP":["California University of Pennsylvania"],
"Cal State":["California State University "],
"Carolina":["University of North Carolina at Chapel Hill", "University of South Carolina"],
"Catholic":["Catholic University of America"],
"Central":["Central State University", "North Carolina Central University"],
"CC":["Colorado College"],
"CCNY":["City College of New York"],
"CCSU":["Central Connecticut State University"],
"CCU":["Coastal Carolina University"],
"CCV":["Community College of Vermont"],
"CGU":["Claremont Graduate University"],
"Chapel Hill":["University of North Carolina at Chapel Hill"],
"Charlotte":["University of North Carolina at Charlotte"],
"Chatt":["University of Tennessee at Chattanooga"],
"Chattanooga":["University of Tennessee at Chattanooga"],
"Chatt State":["Chattanooga State Community College"],
"Chico State":["California State University, Chico"],
"City Tech":["New York City College of Technology"],
"CIA": ["The Culinary Institute of America"],
"CMC":["Claremont McKenna College"],
"CMU":["Carnegie Mellon University", "Central Michigan University"],
"CNU":["Christopher Newport University"],
"Coast Guard":["United States Coast Guard Academy"],
"College Park":["University of Maryland, College Park"],
"Colorado":["University of Colorado Boulder"],
"Colorado Springs":["University of Colorado Colorado Springs"],
"CSB/SJU":["College of Saint Benedict/Saint John's University"],
"CSE":["College of Saint Elizabeth"],
"CSI":["College of Staten Island"],
"CSU":["California State University", "Cleveland State University", "Colorado State University", "Clayton State University", "Coppin State University", "Clark Summit University", "Chicago State University"],
"CSUF":["California State University, Fresno"],
"CSUEB":["California State University, East Bay"],
"CSULA":["California State University, Los Angeles"],
"CSU-Pueblo":["Colorado State University-Pueblo"],
"CSUS":["California State University, Sacramento"],
"CU":["Chapman University", "Clemson University", "University of Colorado at Boulder", "University of Colorado system", "Columbia University", "Cornell University", "Creighton University"],
"CUA":["Catholic University of America"],
"Cumberlands":["University of the Cumberlands"],
"CUNY":["City University of New York"],
"Cuse":["Syracuse University"],
"DC":["Dartmouth College", "Davidson College"],
"De Anza":["De Anza College"],
"DPU":["DePaul University"],
"DSU":["DeSales University", "Dakota State University"],
"DU":["Denison University", "University of Denver", "Drake University", "Drexel University", "Duke University", "Duquesne University"],
"Duke":["Duke University"],
"ECU":["East Carolina University"],
"EIU":["Eastern Illinois University"],
"EMU":["Eastern Mennonite University"],
"EMU":["Eastern Michigan University"],
"ENC":["Eastern Nazarene College"],
"ETSU":["East Tennessee State University"],
"EWU":["Eastern Washington University"],
"EKU":["Eastern Kentucky University"],
"F&M":["Franklin & Marshall College"],
"FAMU":["Florida A&M University"],
"FAU":["Florida Atlantic University"],
"FC":["Founders College"],
"FDU":["Fairleigh Dickinson University"],
"FGCU":["Florida Gulf Coast University"],
"FIU":["Florida International University"],
"Foothill":["Foothill College"],
"FPU":["Fresno Pacific University"],
"Fresno State":["California State University, Fresno"],
"FSU":["Fayetteville State University", "Ferris State University", "Fitchburg State University", "Florida State University", "Framingham State University", "California State University, Fresno", "Frostburg State University"],
"FU":["Fordham University", "Furman University"],
"GB":["University of Wisconsin–Green Bay"],
"GC&SU":["Georgia College & State University"],
"GCSU":["Georgia College & State University"],
"GCU":["Grand Canyon University"],
"Georgia College":["Georgia College & State University"],
"George Mason":["George Mason University"],
"GMU":["George Mason University"],
"Georgia Tech":["Georgia Institute of Technology"],
"George Washington":["George Washington University"],
"GW":["George Washington University"],
"GWU":["George Washington University"],
"GGC":["Georgia Gwinnett College"],
"GONZ":["Gonzaga University"],
"GSU":["Georgia Southern University", "Georgia State University", "Grambling State University"],
"GT":["Georgia Institute of Technology"],
"GVSU":["Grand Valley State University"],
"GW":["Gardner Webb University"],
"GWU":["Gardner Webb University"],
"GU":["Georgetown University"],
"HIU":["Hampton University"],
"HMC":["Harvey Mudd College"],
"Hopkins":["Johns Hopkins University"],
"HU":["Howard University","Hampton University"],
"HSU":["Humboldt State University"],
"IC":["Ithaca College"],
"IIT":["Illinois Institute of Technology"],
"IPFW":["Indiana University-Purdue University Fort Wayne"],
"ISU":["Idaho State University", "Illinois State University", "Indiana State University", "Iowa State University"],
"IU":["Indiana University Bloomington"],
"IUB":["Indiana University Bloomington"],
"IUP":["Indiana University of Pennsylvania"],
"IUPUI":["Indiana University-Purdue University Indianapolis"],
"IWU":["Illinois Wesleyan University"],
"IW":["Iowa Wesleyan University"],
"JHU":["Johns Hopkins University"],
"JMU":["James Madison University"],
"JWU":["Johnson and Wales University"],
"JSU":["Jackson State University"],
"JU":["Jacksonville University"],
"K-State":["Kansas State University"],
"KSU":["Kansas State University", "Kennesaw State University", "Kent State University", "Kentucky State University"],
"KU":["University of Kansas"],
"LA Tech":["Louisiana Tech University"],
"LC":["Louisburg College"],
"LHU":["Lock Haven University"],
"LIU":["Long Island University"],
"LMU":["Lincoln Memorial University", "Loyola Marymount University"],
"Long Beach State":["California State University, Long Beach"],
"LSU":["La Salle University", "Louisiana State University"],
"LSSU":["Lake Superior State University"],
"LTU": ["Lawrence Technological University"],
"Lawrence Tech":["Lawrence Technological University"], 
"LU":["Liberty University", "Lipscomb University", "Lehigh University"],
"LUC":["Loyola University Chicago"],
"Madison":["James Madison University", "University of Wisconsin–Madison"],
"Mary Wash":["University of Mary Washington"],
"Mason":["George Mason University"],
"MCLA":["Massachusetts College of Liberal Arts"],
"Memphis":["University of Memphis"],
"Merchant Marine":["U.S. Merchant Marine Academy"],
"Kings Point":["U.S. Merchant Marine Academy"],
"Merchant Marine, Kings Point":["U.S. Merchant Marine Academy"],
"Metro State":["Metropolitan State College of Denver"],
"MHC":["Mount Holyoke College"],
"MoHo":["Mount Holyoke College"],
"Milwaukee":["University of Wisconsin–Milwaukee"],
"Missouri S&T":["Missouri University of Science and Technology"],
"MIT":["Massachusetts Institute of Technology"],
"Mizzou":["University of Missouri"],
"MMC":["Marymount Manhattan College"],
"Mt. SAC":["Mt. San Antonio College"],
"MSU":["Michigan State University", "Mississippi State University", "Missouri State University", "Morehead State University", "Murray State University", "Montana State University", "Montclair State University", "Mountain State University", "Morgan State University", "University of Missouri"],
"MTSU":["Middle Tennessee State University"],
"MTU":["Michigan Technological University"],
"MU":["Miami University", "Marymount University", "University of Missouri", "Misericordia University", "Millersville University", "Mercyhurst University"],
"Mudd":["Harvey Mudd College"],
"MVille":["Manhattanville College"],
"MVSU":["Mississippi Valley State University"],
"MUW":["Mississippi University for Women"],
"Navy":["U.S. Naval Academy"],
"NAU":["Northern Arizona University", "National American University"],
"NCCU":["North Carolina Central University"],
"NCSU":["North Carolina State University"],
"NC A&T":["North Carolina A&T State University"],
"ND":["University of North Dakota", "University of Notre Dame"],
"NDSU":["North Dakota State University"],
"NE":["Northeastern University"],
"NEU":["Northeastern University"],
"New College":["New College of Florida"],
"NCF":["New College of Florida"],
"NIU":["Northern Illinois University"],
"NKU":["Northern Kentucky University"],
"NMSU":["New Mexico State University"],
"NMU":["Northern Michigan University"],
"NoDak":["University of North Dakota"],
"Nova":["Northern Virginia Community College", "Villanova University"],
"NSU":["Norfolk State University", "Northern State University (South Dakota)", "Northeastern State University (Oklahoma)", "Northwestern State University (Louisiana)", "Nova Southeastern University"],
"NU":["Northeastern University", "University of Nebraska–Lincoln", "Niagara University", "Northwestern University", "Norwich University"],
"NVU":["Northern Vermont University"],
"NW":["Northwestern University"],
"NWMSU":["Northwest Missouri State University"],
"NYIT":["New York Institute of Technology", "New York Tech"],
"NYMC":["New York Medical College"],
"NYU":["New York University"],
"OC":["Oklahoma Christian University"],
"OCC":["Orange Coast College"],
"OCU":["Oklahoma City University"],
"ODU":["Ohio Dominican University", "Old Dominion University"],
"OIT":["Oregon Institute of Technology"],
"OK State":["Oklahoma State University"],
"Ole Miss":["University of Mississippi"],
"ONU":["Ohio Northern University"],
"ORU":["Oral Roberts University"],
"OSU":["Ohio State University", "Oklahoma State University", "Oregon State University"],
"OU":["Oakland University", "Ohio University", "University of Oklahoma", "Oakwood University"],
"Oxy":["Occidental College"],
"Pacific":["University of the Pacific"],
"PC":["Providence College"],
"PCC":["Pasadena City College", "Pensacola Christian College", "Pima Community College", "Polk Community College", "Portland Community College", "Pueblo Community College"],
"Penn":["University of Pennsylvania"],
"Pitt":["University of Pittsburgh"],
"PLNU":["Point Loma Nazarene University"],
"POM":["Pomona College"],
"PSU":["Pennsylvania State University", "Portland State University", "Plymouth State University"],
"PTS":["Princeton Theological Seminary"],
"PVAMU":["Prairie View A&M University"],
"QU":["Quinnipiac University"],
"Reserve":["Case Western Reserve University"],
"RHIT":["Rose-Hulman Institute of Technology"],
"RIC":["Rhode Island College"],
"RISD":["Rhode Island School of Design"],
"RIT":["Rochester Institute of Technology"],
"R-MWC":["Randolph-Macon Woman's College"],
"RPI":["Rensselaer Polytechnic Institute"],
"RU":["Rutgers University"],
"RWU":["Roger Williams University"],
"RWC":["Roberts Wesleyan College"],
"Sacramento State":["California State University, Sacramento"],
"Sac State":["California State University, Sacramento"],
"SBU":["St. Bonaventure University"],
"SC":["University of Southern California", "University of South Carolina"],
"SCSU":["South Carolina State University", "Southern Connecticut State University"],
"Scripps":["Scripps College", "Scripps Institution of Oceanography"],
"SCU":["Santa Clara University"],
"SDSM&T":["South Dakota School of Mines and Technology"],
"SDSU":["South Dakota State University", "San Diego State University"],
"SFSU":["San Francisco State University"],
"SEMo":["Southeast Missouri State University"],
"Sewanee":["University of the South"],
"SHC":["Spring Hill College"],
"SIU": ["Southern Illinois University Carbondale"],
"SIUC":["Southern Illinois University Carbondale"],
"SIUE":["Southern Illinois University Edwardsville"],
"SJC":["St. John's College"],
"SJFC":["St. John Fisher College"],
"SJSU":["San Jose State University"],
"SJU":["Saint Joseph's University", "St. John's University"],
"SLU":["Saint Louis University", "St. Lawrence University", "Saint Leo University"],
"SMC":["St. Mary's College"],
"SMU":["Southern Methodist University"],
"SNHU":["Southern New Hampshire University"],
"SOSU":["Southeastern Oklahoma State University"],
"SPU":["Seattle Pacific University"],
"SRU":["Slippery Rock University of Pennsylvania"],
"Stanislaus State": ["California State University, Stanislaus"],
"Stan State":["California State University, Stanislaus"],
"SSU":["Savannah State University", "California State University, Sonoma"],
"SU":["Southwestern University", "Shenandoah University", "Southern University", "Stanford University", "Susquehanna University", "Syracuse University", "Salisbury University, Samford University"],
"SUI":["State University of Iowa"],
"SUU":["Southern Utah University"],
"SUNY":["State University of New York system"],
"Swat":["Swarthmore College"],
"SWOSU":["Southwestern Oklahoma State University"],
"TAMU":["Texas A&M University"],
"TAMUCC":["Texas A&M University–Corpus Christi"],
"TCNJ":["The College of New Jersey"],
"TCU":["Texas Christian University"],
"Transy":["Transylvania University"],
"TSU":["Tarleton State University", "Tennessee State University", "Texas Southern University", "Truman State University"],
"TTU":["Texas Tech University"],
"TU":["Temple University", "Towson University", "Tufts University", "Tulane University", "Tuskegee University", "University of Tulsa"],
"TxSt":["Texas State University–San Marcos"],
"The U":["University of Miami", "University of Minnesota", "University of Utah", "University of Washington"],
"U of A":["University of Arizona", "University of Arkansas"],
"U of U":["University of Utah"],
"UA":["University of Akron", "University of Alabama", "University of Arizona"],
"UAA":["University of Alaska Anchorage"],
"UAB":["University of Alabama at Birmingham"],
"UAF":["University of Alaska Fairbanks"],
"UAH":["University of Alabama in Huntsville"],
"UALR":["University of Arkansas at Little Rock"],
"UAM":["University of Arkansas at Monticello"],
"UAPB":["University of Arkansas at Pine Bluff"],
"UB":["University of Baltimore", "University at Buffalo"],
"UChicago":["University of Chicago"],
"U of C":["University of Chicago"],
"UC":["University of California system", "University of Chicago", "University of Cincinnati", "University of the Cumberlands"],
"UCB":["University of Colorado Boulder","University of California, Berkeley"],
"UC Berkeley":["University of California, Berkeley"],
"UC Davis":["University of California, Davis"],
"UC Irvine":["University of California, Irvine"],
"UCA":["University of Central Arkansas"],
"UCCS":["University of Colorado Colorado Springs"],
"UCD":["University of California, Davis", "University of Colorado Denver"],
"UCF":["University of Central Florida"],
"UCI":["University of California, Irvine"],
"UCLA":["University of California, Los Angeles"],
"UCM":["University of Central Missouri"],
"UCO":["University of Central Oklahoma"],
"UConn":["University of Connecticut"],
"UCR":["University of California, Riverside"],
"UCSB":["University of California, Santa Barbara"],
"UCSD":["University of California, San Diego"],
"UCSF":["University of California, San Francisco"],
"UD":["University of Dallas", "University of Dayton", "University of Delaware"],
"UDM":["University of Detroit Mercy"],
"UDC":["University of the District of Columbia"],
"U Dub":["University of Washington"],
"UF":["University of Florida"],
"UGA":["University of Georgia"],
"UH":["University of Hawaiʻi at Mānoa", "University of Hawaii system", "University of Houston"],
"U of H":["University of Houston"],
"UHCL":["University of Houston–Clear Lake"],
"UHD":["University of Houston–Downtown"],
"UHS":["University of Houston System"],
"UHV":["University of Houston–Victoria"],
"UI":["University of Idaho", "University of Illinois at Urbana–Champaign", "University of Iowa"],
"U of I":["University of Idaho", "University of Illinois at Urbana–Champaign", "University of Iowa"],
"UIC":["University of Illinois at Chicago"],
"UIUC":["University of Illinois at Urbana–Champaign"],
"UK":["University of Kentucky"],
"ULM":["University of Louisiana at Monroe"],
"UL":["University of Louisiana (at Lafayette)"],
"U of L":["University of Louisville"],
"U of M":["University of Memphis", "University of Miami", "University of Michigan", "University of Minnesota, Twin Cities", "University of Montana"],
"UMass":["University of Massachusetts Amherst"],
"UMB":["University of Maryland, Baltimore", "University of Massachusetts Boston"],
"UMBC":["University of Maryland, Baltimore County"],
"UMC":["University of Missouri–Columbia"],
"UMD":["University of Maryland, College Park", "University of Massachusetts Dartmouth", "University of Michigan–Dearborn", "University of Minnesota Duluth"],
"UMKC":["University of Missouri–Kansas City"],
"UML":["University of Massachusetts Lowell"],
"UMO":["University of Maine at Orono"],
"UMW":["University of Mary Washington"],
"UNA":["University of North Alabama"],
"UNC":["University of North Carolina at Chapel Hill", "University of Northern Colorado"],
"UNCC":["University of North Carolina at Charlotte"],
"UNCG":["University of North Carolina at Greensboro"],
"UNCW":["University of North Carolina at Wilmington"],
"UND":["University of North Dakota"],
"UNF":["University of North Florida"],
"UNH":["University of New Hampshire", "University of New Haven"],
"UNI":["University of Northern Iowa"],
"UNK":["University of Nebraska at Kearney"],
"UNL":["University of Nebraska–Lincoln"],
"UNLV":["University of Nevada, Las Vegas"],
"UNM":["University of New Mexico"],
"UNO":["University of Nebraska at Omaha", "University of New Orleans"],
"UNR":["University of Nevada, Reno"],
"UNT":["University of North Texas"],
"UO":["University of Oregon"],
"UOP":["University of the Pacific"],
"UP":["University of Portland"],
"UPenn":["University of Pennsylvania"],
"UPenn":["University of Pennsylvania"],
"UPIKE":["University of Pikeville"],
"UR":["University of Richmond", "University of Rochester"],
"U of R":["University of Richmond", "University of Rochester"],
"URI":["University of Rhode Island"],
"U of S":["University of Scranton"],
"USA":["University of South Alabama"],
"USAFA":["United States Air Force Academy"],
"USAO":["University of Science and Arts of Oklahoma"],
"USC":["University of Southern California", "University of South Carolina"],
"USCA":["University of South Carolina Aiken"],
"USD":["University of San Diego", "University of South Dakota"],
"USF":["University of San Francisco", "University of South Florida"],
"USFCA":["University of San Francisco"],
"USI":["University of Southern Indiana"],
"USM":["University of Southern Maine", "The University of Southern Mississippi"],
"USU":["Utah State University"],
"UT":["University of Tampa", "University of Tennessee", "University of Texas at Austin", "University of Toledo"],
"UTA":["University of Texas at Arlington"],
"Utah":["University of Utah"],
"UTB/TSC":["University of Texas at Brownsville and Texas Southmost College"],
"UTC":["University of Tennessee at Chattanooga"],
"UTD":["University of Texas at Dallas"],
"UTEP":["University of Texas at El Paso"],
"UTM":["University of Tennessee at Martin"],
"UTPB":["University of Texas of the Permian Basin"],
"UTRGV":["University of Texas Rio Grande Valley"],
"UTSA":["University of Texas at San Antonio"],
"UVA":["University of Virginia"],
"UVM":["University of Vermont"],
"UVU":["Utah Valley University"],
"UW":["University of Washington", "University of Wisconsin system", "University of Wisconsin–Madison", "University of Wyoming"],
"UWF":["University of West Florida"],
"UWG":["University of West Georgia"],
"UWGB":["University of Wisconsin–Green Bay"],
"UWM":["University of Wisconsin–Milwaukee"],
"Valpo":["Valparaiso University"],
"Vandy":["Vanderbilt University"],
"VCU":["Virginia Commonwealth University"],
"Virginia Tech":["Virginia Polytechnic Institute and State University"],
"VMI":["Virginia Military Institute"],
"VPI":["Virginia Polytechnic Institute and State University"],
"VSU":["Valdosta State University", "Virginia State University"],
"VT":["Virginia Polytechnic Institute and State University"],
"VPI":["Virginia Polytechnic Institute and State University"],
"VTC":["Vermont Technical College"],
"VU":["Valparaiso University", "Vanderbilt University", "Villanova University", "Vincennes University", "Vanguard University"],
"W&J":["Washington & Jefferson College"],
"W&L":["Washington and Lee University"],
"W&M":["The College of William & Mary"],
"Wash U":["Washington University in St. Louis"],
"WUSTL":["Washington University in St. Louis"],
"Wazzu":["Washington State University"],
"WC":["Wagner College", "Wilmington College"],
"WCU":["Western Carolina University", "West Chester University"],
"West Point":["U.S. Military Academy"],
"Western":["Western Washington University"],
"WFU":["Wake Forest University"],
"Williams":["Williams College"],
"WIU":["Western Illinois University"],
"WKU":["Western Kentucky University"],
"WMU":["Western Michigan University"],
"WPI":["Worcester Polytechnic Institute"],
"WSU":["Washington State University", "Wichita State University", "Wright State University"],
"WSSU":["Winston-Salem State University"],
"WTAMU":["West Texas A&M University"],
"WVU":["West Virginia University"],
"WVUP":["West Virginia University at Parkersburg"],
"WVU Parkersburg":["West Virginia University at Parkersburg"],
"WWU":["Western Washington University"],
"XU":["Xavier University (Cincinnati)"],
"XULA":["Xavier University of Louisiana"],
"The Y":["Brigham Young University"],
"YSU":["Youngstown State University"],
"YU":["Yeshiva University"]}

def processor(oag,schools,schools_d,colloquial_names):

    # Dictionaries to maintain
    org_map = {}
    non_org = {}
    unis = {}
    
    def is_ascii(s):
        return all(ord(c) < 128 for c in s)

    different_spellings = ['universiteit','universiteit','univerzita','üniversitesi','université','universidad','università','uniwersytet','universidade','universitatea','universität','universitet']

    lowered_colloquial_names = {k.lower(): v for k, v in colloquial_names.items()}
    
    print('Processing ',oag)
    with open(oag,'rt',encoding='utf-8') as f:
        f = csv.reader(f)
        for line in f:
            org = [i for i in line[0].lower().translate({ord(c): None for c in '!@#$,.-;:"/()'}).split() if i not in ['in','at','of','for','studies','all','campuses','main','campus','and','the','&']]
            str_org = ' '.join(org)
            if not len(org):
                continue
            clean_org = None
                            
            if str_org in org_map:
                clean_org = org_map[str_org]
            elif str_org in lowered_colloquial_names:
                clean_orgs = lowered_colloquial_names[str_org]
                if len(clean_orgs) > 1:
                    continue
                else:
                    clean_org = clean_orgs[0]
            elif any(uni in str_org for uni in different_spellings):
                non_org[str_org] = None
                continue
            elif not is_ascii(str_org):
                non_org[str_org] = None
                continue
            elif str_org in non_org:
                continue
            else:
                org = set(org)
                matches = []
                idx = 0
                for school in schools: #passed in 
                    if len(org & school) in [len(org),len(school)]:
                        matches.append((school,idx))
                    idx += 1
                if not matches:
                    non_org[str_org] = None
                    continue
                top = 1.0
                top_i = 0
                if len(matches) > 1:
                    counter = 0
                    for m in matches:
                        overlap = float(len(org & m[0]))
                        left = overlap / float(len(org))
                        right = overlap / float(len(m[0]))
                        diff = abs(left-right)
                        if diff < top:
                            top = abs(left-right)
                            top_i = counter
                        counter += 1
                clean_org = schools_d[matches[top_i][1]][1]
                org_map[str_org] = clean_org
            
            # Create entry if it doesn't exist
            #print((clean_org))
            if clean_org not in unis:
                unis[clean_org] = []
            else:
                unis[clean_org].append(str_org)
                
    return org_map, non_org, unis

matches = []
for index, row in universities.iterrows():
    name = row['name']
    
    if name in org_map:
        matches.append(org_map[name])
    else:
        matches.append(None)

universities['match'] = matches


# # Write to csv

universities.to_csv("/Users/jacquelinewood/Documents/URAP/Matching/matched_universities.csv")

