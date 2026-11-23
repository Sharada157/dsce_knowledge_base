# DSCE Knowledge Base (for the admissions and student support chatbot)

Source: https://www.dsce.edu.in (public website of Dayananda Sagar College of Engineering, Bengaluru)
Collected: 23 Nov 2026 with Firecrawl (map + scrape). Every file has the source URL in its YAML front-matter (`source_url`), plus `category`, `retrieved`, `retrieval_method` and optional `notes`.
`_manifest.csv` lists every file with its source URL. This is an unofficial student project; always verify with the college office.

## Files

### 01_admissions
- `01_admissions/admissions-overview.md`: Admissions Overview, Eligibility and Procedure (BE, M.Tech, MBA, MCA, Ph.D) (html)
- `01_admissions/fees-be-comedk-quota-2026-27.md`: 1st Year B.E. COMED-K Quota: Admission Process and Fee Details 2026-27 (pdf)
- `01_admissions/fees-be-kea-cet-quota-2026-27.md`: 1st Year B.E. KEA/CET Quota: Admission Process and Fee Details 2026-27 (pdf)
- `01_admissions/fees-be-management-quota-2026-27.md`: 1st Year B.E. Management Quota: Tuition Fees and Eligibility 2026-27 (pdf)
- `01_admissions/fees-pg-mba-mca-mtech-pgcet-2026-27.md`: MBA, MCA and M.Tech PGCET Quota: Admission Process and Fee Details 2026-27 (pdf)

### 02_academics
- `02_academics/examination-section.md`: Examination Section: Overview, Circulars and Contact (html)
- `02_academics/official-document-index.md`: Index of Official DSCE Documents and PDFs Discovered (not yet parsed) (html)
- `02_academics/ug-calendar-of-events-2026-27.md`: UG Calendar of Events 2026-27 (1st, 3rd, 5th and 7th Semester) (pdf)

### 03_campus_placements
- `03_campus_placements/contacts-directory.md`: Contact Directory: Offices, Hostels, Fee, Scholarship, Library, Placement and HODs (html)
- `03_campus_placements/grievance-and-statutory-committees.md`: Grievance Redressal, Anti-Ragging and Statutory Committees (html)
- `03_campus_placements/library.md`: Library: Timings, Collection and Services (html)
- `03_campus_placements/placements-cse-statistics.md`: CSE Department Placement Statistics 2021-22 to 2024-25 (html)
- `03_campus_placements/placements-overview.md`: Placements: Overview, Training and Contact (html)
- `03_campus_placements/scholarships.md`: Scholarships Available to DSCE Students (html)

### 04_accreditation
- `04_accreditation/accreditation-summary.md`: Accreditation and Approvals Summary (NAAC, NBA, AICTE, UGC, VTU) (html)
- `04_accreditation/naac-and-iqac.md`: NAAC Accreditation and Internal Quality Assurance Cell (IQAC) (html)
- `04_accreditation/nirf-reports.md`: NIRF Reports (2024, 2025, 2026) (html)

### 05_student_faq
- `05_student_faq/student-faq.md`: Student-Contributed Campus FAQ (40 Q&As on campus culture, hostel, mess, attendance 85/75 rule, clubs like Point Blank, fests like Furore, canteen, metro, BMTC 15-E, placements, hacks) (faq)

## Coverage against the request
| Area | Status |
|---|---|
| Admissions: BE, M.Tech, MBA, MCA, Ph.D eligibility and procedure | Covered (admissions page) |
| Fees and admission process 2026-27 (KEA, COMEDK, Management, PG) | Covered. Lateral entry (DCET) 2026-27 PDF not yet parsed |
| Intake per program | NOT covered. Intake is not on the admissions page; it is on department pages and the AICTE mandatory disclosure PDF |
| Academic calendar | UG odd-semester 2026-27 covered. PG calendar PDF not yet parsed |
| Autonomous regulations / examination guidelines | Exam section page covered. Detailed grading, CIE/SEE, IATs and 85/75 attendance rules covered in student FAQ. |
| Department-wise syllabus PDFs | NOT parsed. URLs are indexed in `02_academics/official-document-index.md` |
| Placement statistics | CSE department stats + comprehensive placement realities across branches covered in student FAQ. |
| Hostel facilities | Detailed in student FAQ (Indian vs NRI, curfew 9PM/10PM, mess timings, outpass, off-campus PGs). Phone numbers in contacts. |
| Library hours | Covered |
| Scholarships | Covered |
| Grievance redressal contacts | Covered (committees and emails) |
| NAAC / IQAC | Covered |
| NIRF | Report titles only; PDFs and rank values not captured |
| NBA | Certificate page is an image; program list not captured |

## Known data issues (important for chatbot answers)
1. **Hostel phone numbers differ across documents.** The Contact Us page lists NRI Boys Hostel 080-42161745 and Girls Hostel 080-42161727. The 2026-27 PG document lists Girls Hostel 080-42162727 and NRI Boys 080-42162745, and the COMEDK/Management PDFs use 080-42162745 for NRI Boys.
2. **Management quota eligibility conflicts.** The admissions page says 50% in PCM; the 2026-27 management quota PDF says 70% in 10th Maths and Science and 65% in 12th pre-board Maths and Physics. Both are stored with a note.
3. **Typo in a PDF email domain** ("dayonandasagar.edu"); the site's official domain is dayanandasagar.edu and it has been corrected in the file with a note.
4. **Calendar oddities:** the first-semester IAT-2 marks display date is listed twice in the source (12 Nov and 3 Dec), and the 7th-semester exam start is printed as 2027 (probably 2026). Both are flagged in the file.
5. **NAAC validity:** the IQAC page lists Cycle II CGPA 3.20 valid till 27 June 2027 and an older CGPA 3.42 valid till 10 July 2021. Quote the dates with the cycle.
6. **CSE placement table:** column headers were not captured, so the figures are stored as raw rows and must not be interpreted until checked on the source page.
7. Fees and dates change every year; re-run the collection before each admission season.

## Extraction notes
- The site does not use semantic HTML tags, so the navigation menu could not be stripped by tag. HTML pages were captured either with Firecrawl's targeted query (main content only) or as markdown with the menu removed by hand.
- PDFs were parsed with Firecrawl's PDF parser; some PDF headers were garbled by the extraction and are flagged in `notes`.
- The site map returned many mangled duplicate URLs (long repeated path segments) and mirror subdomains (for example developer.dsce.edu.in); these were ignored.
