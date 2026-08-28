# Day 8 - Set For Life Manual QA Sample Sheet

Five draws selected from the collected dataset, manually compared against the official source:

https://www.national-lottery.co.uk/results/set-for-life/draw-details?drawNo=<draw_number>


| Draw ID              | DB Date          | DB Numbers (Main + LB) | Official Site Match |
|-----------------------|------------------|------------------------|----------------------|
| SET-FOR-LIFE-778      | Thu 27 Aug 2026  | 1, 24, 28, 31, 47 (LB: 3) | ✅ Match             |
| SET-FOR-LIFE-777      | Mon 24 Aug 2026  | 11, 19, 28, 38, 43 (LB: 9) | ✅ Match             |
| SET-FOR-LIFE-776      | Thu 20 Aug 2026  | 6, 9, 29, 32, 47 (LB: 9) | ✅ Match             |
| SET-FOR-LIFE-775      | Mon 17 Aug 2026  | 13, 14, 23, 33, 36 (LB: 10) | ✅ Match             |
| SET-FOR-LIFE-774      | Thu 13 Aug 2026  | 4, 5, 10, 12, 36 (LB: 8) | ✅ Match             |

## Method
Each draw number was opened directly at:
`https://www.national-lottery.co.uk/results/set-for-life/draw-details?drawNo=<N>`
and the displayed date and numbers were compared by eye against the values stored in the database.

## Result
5 out of 5 draws matched exactly. No discrepancies found.