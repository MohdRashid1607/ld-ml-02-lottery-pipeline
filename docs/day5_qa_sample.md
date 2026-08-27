# Day 5 - Manual QA Sample Sheet

Ten draws randomly selected from the collected dataset, manually
compared against the official source: 
https://www.national-lottery.co.uk/results/euromillions/draw-details?drawNo=<draw_number>

| Draw ID              | DB Date          | DB Main Numbers      | Official Site Match |
|-----------------------|------------------|------------------------|----------------------|
| EUROMILLIONS-1924     | Fri 27 Feb 2026  | 14, 24, 27, 39, 42     | ✅ Match             |
| EUROMILLIONS-1930     | Fri 20 Mar 2026  | 5, 12, 16, 37, 46      | ✅ Match             |
| EUROMILLIONS-1938     | Fri 17 Apr 2026  | 22, 23, 28, 41, 47     | ✅ Match             |
| EUROMILLIONS-1945     | Tue 12 May 2026  | 4, 26, 32, 35, 36      | ✅ Match             |
| EUROMILLIONS-1950     | Fri 29 May 2026  | 5, 14, 18, 31, 35      | ✅ Match             |
| EUROMILLIONS-1958     | Fri 26 Jun 2026  | 6, 16, 26, 34, 35      | ✅ Match             |
| EUROMILLIONS-1963     | Tue 14 Jul 2026  | 10, 19, 37, 42, 47     | ✅ Match             |
| EUROMILLIONS-1968     | Fri 31 Jul 2026  | 10, 24, 25, 31, 45     | ✅ Match             |
| EUROMILLIONS-1970     | Fri 07 Aug 2026  | 26, 29, 35, 38, 47     | ✅ Match             |
| EUROMILLIONS-1974     | Fri 21 Aug 2026  | 10, 14, 15, 19, 45     | ✅ Match             |

## Method
Each draw number was opened directly at:
`https://www.national-lottery.co.uk/results/euromillions/draw-details?drawNo=<N>`
and the displayed date and main numbers were compared by eye against
the values stored in the database.

## Result
10 out of 10 draws matched exactly. No discrepancies found in dates
or main numbers.
