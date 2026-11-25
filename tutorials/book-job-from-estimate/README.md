# Book a job from an approved estimate

**For:** office staff (made for Stephanie). **Problem:** an estimate shows Approved but nothing is on the schedule; she needs to turn it
into a booked job with a date, time and crew.

| Step | On screen | Narration |
|---|---|---|
| Intro | How to book a job · from an approved estimate · 7 steps | Here's how to book a job from an approved estimate. It takes seven quick steps. |
| 1 | Go to Sales and search the estimate number | First, click Sales in the menu on the left. Then type the estimate number into the search box. Here, it's twenty-two eleven. |
| 2 | Open the estimate | On the estimate's card, click Preview. In the window that opens, click Open estimate. |
| 3 | Click Book job | The estimate says Accepted, not booked. Click the dark Book job button on the right. |
| 4 | Click a free time on the calendar | Now click a free time on the calendar on the right. The start date and start time fill in for you. |
| 5 | Assign your crew | Scroll down to Assign To, and click it. Pick each person who's working the job. |
| 6 | Choose whether the customer is notified | Leave Notify customer on, and they'll get a confirmation. Turn it off if you'd rather tell them yourself. |
| 7 | Click Book Job to save | Once a date and time are picked, Book Job turns dark. Click it to save the job. And that's it. You're done. |
| Done | The job is booked. It now shows on the schedule with your crew. | (chime) |

Rebuild: `python3 standard/render_tutorial.py tutorials/book-job-from-estimate --format both`, then `python3 standard/gates.py tutorials/book-job-from-estimate`.

Privacy: customer name, address and crew roster were blurred in the source; the renderer also blurs the pipeline value, estimate
amounts, the salesperson chip and the person filter (see `privacy` in tutorial.json). Source: `source/walkthrough.gif`.
