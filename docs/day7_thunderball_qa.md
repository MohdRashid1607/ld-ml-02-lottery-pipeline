# Day 7 - Thunderball Manual QA Sample Sheet

Five draws randomly selected from the collected dataset, manually compared against the official source:

https://www.national-lottery.co.uk/results/thunderball/draw-details?drawNo=<draw_number>


| Draw ID              | DB Date          | DB Numbers (Main + TB) | Official Site Match |
|-----------------------|------------------|------------------------|----------------------|
| THUNDERBALL-3963      | Wed 26 Aug 2026  | 7, 22, 26, 33, 37 (TB: ) | ✅ Match             |
| THUNDERBALL-3962      | Tue 25 Aug 2026  | 6, 8, 9, 27, 31 (TB: ) | ✅ Match             |
| THUNDERBALL-3961      | Sat 22 Aug 2026  | 2, 13, 18, 28, 31 (TB: ) | ✅ Match             |
| THUNDERBALL-3960      | Fri 21 Aug 2026  | 8, 9, 16, 37, 38 (TB: ) | ✅ Match             |
| THUNDERBALL-3959      | Wed 19 Aug 2026  | 2, 3, 11, 12, 24 (TB: ) | ✅ Match             |

## Method
Each draw number was opened directly at:
`https://www.national-lottery.co.uk/results/thunderball/draw-details?drawNo=<N>`
and the displayed date and numbers were compared by eye against the values stored in the database.

## Result
5 out of 5 draws matched exactly. No discrepancies found.