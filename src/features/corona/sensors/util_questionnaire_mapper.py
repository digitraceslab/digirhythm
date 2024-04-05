# -*- coding: utf-8 -*-
ucla_3_items_map = {
    "In the late stages of the pandemic; how often did you feel that you lack companionship?": "UCLA3_1_late",
    "In the late stages of the pandemic; how often did you feel left out?": "UCLA3_2_late",
    "In the late stages of the pandemic; how often did you feel isolated from others?": "UCLA3_3_LATE",
}

phq2_map = {
    "Little interest or pleasure in doing things.": "PHQ2_1",
    "Feeling down; depressed or hopeless.": "PHQ2_2",
}

phq2_map = {
    "Little interest or pleasure in doing things.": "PHQ2_1",
    "Feeling down; depressed or hopeless.": "PHQ2_2",
}

psqi_map = {
    "Currently; is your sleep typically interrupted? (For example; for attending to a child or due to loud neighbours or medical reasons.)": "PSQI_Disturbance",
    "During the last month; was your sleep typically interrupted? (For example; for attending to a child or due to loud neighbours or medical reasons.)": "PSQI_Disturbance",
    "During the past month; how often have you taken medicine (prescribed or “over the counter”) to help you sleep?": "PSQI_Medication_Use",
    "During the past month; how often have you had trouble staying awake while driving; eating meals; or engaging in social activity?": "PSQI_Daytime_Dysfunction_1",
    "During the past month; how much of a problem has it been for you to keep up enthusiasm to get things done?": "PSQI_Daytime_Dysfunction_2",
    "During the past month; how would you rate your sleep quality overall?": "PSQI_Sleep_Quality",
    #    'When have you usually gone to bed? (hh:mm)' : 'PSQI_6',
    #    'What time have you usually gotten up in the morning? (hh:mm)' : 'PSQI_7',
    #    'How long (in minutes) has it taken you to fall asleep each night?' : 'PSQI_8',
    #    'How many hours of actual sleep did you get at night?' : 'PSQI_9',
    "During the past month; have you experienced nightmares (unpleasant or scary dreams)?": "PSQI_Efficiency",
}

pss10_map = {
    "In the last month; how often have you been upset because of something that happened unexpectedly?": "PSS10_1",
    "In the last month; how often have you felt that you were unable to control the important things in your life?": "PSS10_2",
    "In the last month; how often have you felt nervous and “stressed”?": "PSS10_3",
    "In the last month; how often have you felt confident about your ability to handle your personal problems?": "PSS10_4",
    "In the last month; how often have you felt that things were going your way?": "PSS10_5",
    "In the last month; how often have you been able to control irritations in your life?": "PSS10_6",
    "In the last month; how often have you felt that you were on top of things?": "PSS10_7",
    "In the last month; how often have you been angered because of things that were outside of your control?": "PSS10_8",
    "In the last month; how often have you felt difficulties were piling up so high that you could not overcome them?": "PSS10_9",
}

# There are two different PANAS questionnaires in the survey: one is intended for pre-pandemic measurement and one is for
# during-pandemic measurement
panas_map = {
    "Upset": "PANAS_NEG_Pre_Upset",
    "Hostile": "PANAS_NEG_Pre_Hostile",
    "Alert": "PANAS_POS_Pre_Alert",
    "Ashamed": "PANAS_NEG_Pre_Ashamed",
    "Inspired": "PANAS_POS_Pre_Inspired",
    "Nervous": "PANAS_NEG_Pre_Nervous",
    "Determined": "PANAS_POS_Pre_Determined",
    "Attentive": "PANAS_POS_Pre_Attentive",
    "Afraid": "PANAS_NEG_Pre_Afraid",
    "Active": "PANAS_POS_Pre_Active",
    "Upset.1": "PANAS_NEG_During_Upset",
    "Hostile.1": "PANAS_NEG_During_Hostile",
    "Alert.1": "PANAS_POS_During_Alert",
    "Ashamed.1": "PANAS_NEG_During_Ashamed",
    "Inspired.1": "PANAS_POS_During_Inspired",
    "Nervous.1": "PANAS_NEG_During_Nervous",
    "Determined.1": "PANAS_POS_During_Determined",
    "Attentive.1": "PANAS_POS_During_Attentive",
    "Afraid.1": "PANAS_NEG_During_Afraid",
    "Active.1": "PANAS_POS_During_Active",
}

big5_map = {
    "Tends to be quiet.": "BIG5_Extraversion_1R",
    "Is compassionate; has a soft heart.": "BIG5_Agreeableness_2",
    "Tends to be disorganized.": "BIG5_Conscientiousness_3R",
    "Worries a lot.": "BIG5_Neuroticism_4",
    "Is fascinated by art; music; or literature.": "BIG5_Openness_5",
    "Is dominant; acts as a leader.": "BIG5_Extraversion_6",
    "Is sometimes rude to others.": "BIG5_Agreeableness_7R",
    "Has difficulty getting started on tasks.": "BIG5_Conscientiousness_8R",
    "Tends to feel depressed; blue.": "BIG5_Neuroticism_9",
    "Has little interest in abstract ideas.": "BIG5_Openness_10R",
    "Is full of energy.": "BIG5_Extraversion_11",
    "Assumes the best about people.": "BIG5_Agreeableness_12",
    "Is reliable; can always be counted on.": "BIG5_Conscientiousness_13",
    "Is emotionally stable; not easily upset.": "BIG5_Neuroticism_14R",
    "Is original; comes up with new ideas.": "BIG5_Openness_15",
}


meq_map = {
    "Approximately what time would you get up if you were entirely free to plan your day? (choose the closest if your time is outside of the ranges below.)": "MEQ_1",
    "During the first half hour after you wake up in the morning; how do you feel?": "MEQ_2",
    "At approximately what time in the evening do you feel tired; and; as a result; in need of sleep?": "MEQ_3",
    "At approximately what time of day do you usually feel your best?": "MEQ_4",
    "One hears about “morning-types” and “evening-types.” Which one of these types do you consider yourself to be?": "MEQ_5",
}

gad2_map = {
    "Feeling nervous; anxious or on edge.": "GAD2_1",
    "Not being able to stop or control worrying.": "GAD2_2",
}

# Utilities question map
months = [
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
    "January",
    "February",
    "March",
    "April",
    "May",
]
utils_map = {
    "user": "subject_id",
    "What is your current role at Aalto?": "occupation",
    "Age:": "age",
    "Where are you from?": "origin",
    "Gender": "gender",
    "How many children (under 18 years old) do you live with?": "children_at_home",
    "How many other adults (over 18 years old) do you live with?": "adults_at_home",
    "How many doses of COVID-19 vaccine have you received so far?": "CovidDoses",
    "Prior to the pandemic what percentage of your working time did you spend on site (e.g. Aalto Campus if you were an Aalto employee)?": "prior_perc_time_onsite",
    "During the pandemic what percentage of your working time did you spend on site (e.g. Aalto Campus if you were an Aalto employee)?": "early_perc_time_onsite",
    "In the past two months what have been your main sources of stress? (e.g. health; going back to campus for working or teaching; etc)": "stress_sources_comment",  # past 2 months
    "In the past month what have been your main sources of stress? (e.g. health; going back to campus for working or teaching; etc)": "stress_sources_comment",  # past month
    "Snoozing can be considered as choosing to go back to sleep after an alarm has awakened you intending to wake up later; setting an alarm earlier than when you intend to wake up; or setting multiple alarms with the intent to not wake up on the first alarm. Do you currently consider yourself a snoozer using this definition?": "snoozer_current",
    "Were you a snoozer in the two years prior to the pandemic? (i.e. years 2018; 2019; and early 2020)": "snoozer_prior",
    "How do you feel about the state of the pandemic around you (NOT globally). Please choose all that apply.": "pandemic_comment",
    "How do you feel about latest policies of the Aalto University with respect to COVID-19?": "policies_comment",
    "If you have any further comments or information that you would like to add (with respect to any aspect of the study) please write them in the box below. Make sure not to add any personal information that might directly or indirectly identify you (e.g. name; email; etc.) in this field. The information you add here will be used as research data.": "misc_comment",
}

for month in months:
    colname1 = "If you worked in (part of) {} what percentage of your working time did you spend on site (i.e. Aalto Campus)? (do not answer if you did not work at all in {}).".format(
        month, month
    )
    colname2 = "How many days in *{}* were you on vacation or on sick leave?".format(
        month
    )
    colname3 = "How many days in {} were you on vacation or on sick leave?".format(
        month
    )
    utils_map[colname1] = "PercTimeSpentOnsite"
    utils_map[colname2] = "DayOnLeave"
    utils_map[colname3] = "DayOnLeave"

# Answer map

UCLA_3_ITEM_MAP = {"hardly-ever": 1, "some-of-the-time": 2, "often": 3}

PSS_ANSWER_MAP = {
    "never": 0,
    "almost-never": 1,
    "sometimes": 2,
    "fairly-often": 3,
    "very-often": 4,
}

PSS_REVERT_ANSWER_MAP = {
    "never": 4,
    "almost-never": 3,
    "sometimes": 2,
    "fairly-often": 1,
    "very-often": 0,
}

BIG5_ANSWER_MAP = {
    "disagree-strongly": 1,
    "disagree-a-little": 2,
    "neutral-no-opinion": 3,
    "agree-a-little": 4,
    "agree-strongly": 5,
}

BIG5_REVERT_ANSWER_MAP = {
    "disagree-strongly": 5,
    "disagree-a-little": 4,
    "neutral-no-opinion": 3,
    "agree-a-little": 2,
    "agree-strongly": 1,
}

PANAS_ANSWER_MAP = {
    "very-slightly-or-not-at-all": 0,
    "a-little": 1,
    "moderately": 2,
    "quite-a-bit": 3,
    "extremely": 4,
}

PHQ2_ANSWER_MAP = {
    "not-at-all": 0,
    "several-days": 1,
    "more-than-half-the-days": 2,
    "nearly-every-day": 3,
}

PSQI_ANSWER_MAP = {
    "not-during-the-past-month": 0,
    "less-than-once-a-week": 1,
    "once-or-twice-a-week": 2,
    "three-or-more-times-a-week": 3,
    "very-good": 0,
    "fairly-good": 1,
    "fairly-bad": 2,
    "very-bad": 3,
    "not-on-most-nights": 0,
    "yes-sometimes": 1,
    "yes-almost-every-night": 2,
}

MEQ_1_ANSWER_MAP = {
    "500630-am": 5,
    "630745-am": 4,
    "745945-am": 3,
    "9451100-am": 2,
    "110012-noon": 1,
}

MEQ_2_ANSWER_MAP = {
    "very-tired": 1,
    "fairly-tired": 2,
    "fairly-refreshed": 3,
    "very-refreshed": 4,
}

MEQ_3_ANSWER_MAP = {
    "800900-pm": 5,
    "9001015-pm": 4,
    "10151245-am": 3,
    "1245200-am": 2,
    "200300-am": 1,
}

MEQ_4_ANSWER_MAP = {
    "10-pm5-am": 1,
    "510-pm": 2,
    "10-am5-pm": 3,
    "810-am": 4,
    "58-am": 5,
}

MEQ_5_ANSWER_MAP = {
    "definitely-a-morning-type": 6,
    "rather-more-a-morning-type-than-an-evening-type": 4,
    "rather-more-an-evening-type-than-a-morning-type": 2,
    "definitely-an-evening-type": 0,
}
