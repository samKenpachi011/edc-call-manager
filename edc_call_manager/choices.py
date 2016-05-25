from .constants import NO_CONTACT


CONTACT_TYPE = (
    ('direct', 'Direct contact with participant'),
    ('indirect', 'Contact with person other than participant'),
    (NO_CONTACT, 'No contact made'),
)

APPT_LOCATIONS = (
    ('home', 'At home'),
    ('work', 'At work'),
    ('clinic', 'At clinic'),
    ('OTHER', 'Other location'),
)


APPT_GRADING = (
    ('firm', 'Firm appointment'),
    ('weak', 'Possible appointment'),
    ('guess', 'Estimated by RA'),
)
