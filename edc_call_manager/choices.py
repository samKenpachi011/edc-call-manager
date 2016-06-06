from .constants import NO_CONTACT, DIRECT_CONTACT, INDIRECT_CONTACT


CONTACT_TYPE = (
    (DIRECT_CONTACT, 'Direct contact with participant'),
    (INDIRECT_CONTACT, 'Contact with person other than participant'),
    (NO_CONTACT, 'No contact made'),
)

APPT_LOCATIONS = (
    ('home', 'At home'),
    ('work', 'At work'),
    ('telephone', 'By telephone'),
    ('clinic', 'At clinic'),
    ('OTHER', 'Other location'),
)


APPT_GRADING = (
    ('firm', 'Firm appointment'),
    ('weak', 'Possible appointment'),
    ('guess', 'Estimated by RA'),
)
