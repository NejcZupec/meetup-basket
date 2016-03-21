import logging

from django.db import models

logger = logging.getLogger("meetup_basket")


class Season(models.Model):
    """
    Each row represents a season.
    """
    name = models.CharField(max_length=255, unique=True)
    slug = models.CharField(max_length=255, unique=True, blank=True, null=True)

    def __unicode__(self):
        return "Season (name=%s, slug=%s)" % (self.name, self.slug)


class Group(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    url_name = models.CharField(max_length=255)
    timezone = models.CharField(max_length=255)

    def __unicode__(self):
        return "Group <%s> (id=%s, url_name=%s)" % (self.name, self.id, self.url_name)


class Member(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    group = models.ForeignKey("meetup_integration.Group")
    height = models.PositiveIntegerField(default=0)

    def meetups_attended(self, season):
        if season.slug == "all":
            return Attendance.objects.filter(
                member=self,
                attendance=True,
            ).count()
        else:
            return Attendance.objects.filter(
                member=self,
                attendance=True,
                event__season=season,
            ).count()

    def count_wins(self, season):
        events = Event.objects.all() if season.slug == "all" else Event.objects.filter(season=season)
        return sum([team.match_win for team in Team.objects.filter(members__id__exact=self.id, event__in=events)])

    def count_loses(self, season):
        events = Event.objects.all() if season.slug == "all" else Event.objects.filter(season=season)
        return sum([team.match_lose for team in Team.objects.filter(members__id__exact=self.id, event__in=events)])

    def games_played(self, season):
        return self.count_wins(season) + self.count_loses(season)

    def win_lose_coefficient(self, season):
        if self.games_played(season) > 0:
            return float(self.count_wins(season))/self.games_played(season)
        else:
            return 0.5

    def weight(self, event):
        from web.utils import calculate_weight

        attended = event.member_attended(self)
        rsvp = event.get_member_rsvp(self)

        return float(calculate_weight(attended, rsvp))

    def coefficient_for_events(self, events):
        wins = 0.0
        loses = 0.0

        for event in events:
            for team in event.get_teams():
                if self in team.get_members():
                    wins += team.match_win
                    loses += team.match_lose

        if wins + loses > 0:
            return float(wins/(wins+loses))
        else:
            return 0.5

    def coefficient_after_event(self, event, season):
        try:
            return Coefficient.objects.get(event=event, member=self, season=season).coefficient
        except:
            return 0.0

    def basket_diff(self, season):
        event = Event.objects.filter(status="past").latest("start_date") if season.slug == "all" else Event.objects.filter(
            season=season,
            status="past",
        ).latest("start_date")
        return self.basket_diff_after_event(event, season)

    def basket_diff_avg(self, season):
        if self.games_played(season) > 0:
            return self.basket_diff(season)/self.games_played(season)
        else:
            return 0.0

    def basket_diff_for_events(self, events):
        diff = 0
        for event in events:
            diff += event.get_diff_for_member(self)
        return diff

    def basket_diff_after_event(self, event, season):
        try:
            return Coefficient.objects.get(event=event, member=self, season=season).basket_diff
        except:
            logger.error("Coefficient doesn't exist.")
            return 0.0

    def hall_rent_for_season(self, season):
        return Payment.objects.filter(member=self, event__season=season).\
            aggregate(costs=models.Sum("price")).get("costs", 0.0)

    def costs_for_season(self, season):
        return self.meetup_fee_for_season(season) + self.hall_rent_for_season(season)

    def contribution_for_season(self, season):
        c = Transaction.objects.filter(season=season, type="membership_fee", member=self).\
            aggregate(membership_fee=models.Sum("amount")).get("membership_fee", 0.0)
        return c if c else 0.0

    def balance_for_season(self, season):
        return self.contribution_for_season(season) - self.costs_for_season(season)

    def membership_fee_for_season(self, season):
        balance = self.balance_for_season(season)
        fee = round(balance + balance*0.3)
        return int(5 * round(float(fee)/5)) * -1.0 if fee < 0 else 0.0  # round fee to 5 EUR

    @staticmethod
    def meetup_fee_for_season(season):
        members_count = float(Member.objects.all().count())
        meetup_fee = Transaction.objects.filter(season=season, type="meetup_fee").\
            aggregate(meetup_fee=models.Sum("amount")).get("meetup_fee", 0.0)
        meetup_fee = meetup_fee if meetup_fee else 0.0
        return meetup_fee/members_count * -1 if members_count > 0 else 0.0

    def __unicode__(self):
        return "Member <%s> (status=%s)" % (self.name, self.status)


class Event(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    event_url = models.CharField(max_length=255)
    group = models.ForeignKey(Group)
    status = models.CharField(max_length=255)
    season = models.ForeignKey("meetup_integration.Season")
    start_date = models.DateTimeField()

    def get_members_with_rsvp(self, response="yes"):
        return [rsvp.member for rsvp in RSVP.objects.filter(event=self, response=response)]

    def member_attended(self, member):
        try:
            return Attendance.objects.get(event=self, member=member).attendance
        except Attendance.DoesNotExist:
            return False

    def weight(self):
        return sum([member.weight(self) for member in Member.objects.all()])

    def get_member_rsvp(self, member):
        try:
            return RSVP.objects.get(event=self, member=member).response
        except RSVP.DoesNotExist:
            return None

    def sequence_number(self):
        try:
            prefix = self.name.split(" ")[2]
            sn = prefix.split("#")[1]
        except Exception:
            print Exception
            sn = ""
        return sn

    def get_teams(self):
        return Team.objects.filter(event=self)

    def get_matches(self):
        return Match.objects.filter(team_a__event=self, team_b__event=self)

    def get_diff_for_member(self, member):
        diff = 0
        for match in self.get_matches():
            diff += match.diff_for_member(member)
        return diff

    def __unicode__(self):
        return "Event <%s> (status=%s)" % (self.name, self.status)

    class Meta:
        ordering = ["-start_date"]


class Attendance(models.Model):
    attendance = models.BooleanField(default=True)
    rsvp = models.CharField(max_length=255)
    event = models.ForeignKey("meetup_integration.Event")
    member = models.ForeignKey("meetup_integration.Member")

    def __unicode__(self):
        return "Attendance for %s (attendance=%s, rsvp=%s, event=%s)" % (self.member.name,
                                                                         self.attendance,
                                                                         self.rsvp,
                                                                         self.event.name,)


class Team(models.Model):
    name = models.CharField(max_length=255)
    event = models.ForeignKey("meetup_integration.Event")
    members = models.ManyToManyField(Member)
    match_win = models.IntegerField(default=0)
    match_lose = models.IntegerField(default=0)

    def get_members(self):
        return self.members.all()

    def __unicode__(self):
        return "Team <%s> (event=%s, match_win=%d, match_lose=%d)" % (self.name,
                                                                      self.event.name,
                                                                      self.match_win,
                                                                      self.match_lose,)


class RSVP(models.Model):
    id = models.IntegerField(primary_key=True)
    response = models.CharField(max_length=255)
    event = models.ForeignKey("meetup_integration.Event")
    member = models.ForeignKey("meetup_integration.Member")

    def __unicode__(self):
        return "RSVP <%s> (event=%s, member=%s)" % (self.response, self.event.name, self.member.name)


class Coefficient(models.Model):
    """
    Coefficient for each member after specific meetup (event).
    """
    member = models.ForeignKey("meetup_integration.Member")
    event = models.ForeignKey("meetup_integration.Event")
    coefficient = models.FloatField(default=0.5)
    basket_diff = models.FloatField(default=0.0)
    season = models.ForeignKey("meetup_integration.Season")

    def __unicode__(self):
        return "Coefficient (member=%s, event=%s, coef=%f)" % (self.member, self.event, self.coefficient)

    class Meta:
        unique_together = ("member", "event", "season")


class Payment(models.Model):
    member = models.ForeignKey("meetup_integration.Member")
    event = models.ForeignKey("meetup_integration.Event")
    price = models.FloatField(default=0.0)

    def __unicode__(self):
        return "Payment (member=%s, event=%s, price=%f.2)" % (self.member.name, self.event.name, self.price)

    class Meta:
        unique_together = ("member", "event")


class Transaction(models.Model):
    TRANSACTION_TYPE = (
        ('membership_fee', 'Membership Fee'),
        ('meetup_fee', 'Meetup Fee'),
        ('hall_rent', 'Hall Rent'),
    )

    date = models.DateField(help_text="When a transaction has been executed.")
    description = models.CharField(max_length=255, null=True, blank=True)
    amount = models.FloatField()
    member = models.ForeignKey(Member, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    season = models.ForeignKey(Season)

    def __unicode__(self):
        return "Transaction (amount: %f, date: %s)" % (self.amount, self.date)


class Match(models.Model):
    team_a = models.ForeignKey("meetup_integration.Team", related_name="team_a")
    team_b = models.ForeignKey("meetup_integration.Team", related_name="team_b")
    points_a = models.PositiveIntegerField(default=0)
    points_b = models.PositiveIntegerField(default=0)

    def diff_for_member(self, member):
        if member in self.team_a.members.all():
            return self.points_a - self.points_b
        if member in self.team_b.members.all():
            return self.points_b - self.points_a
        return 0

    def __unicode__(self):
        return "Match (%s [%d : %d] %s)" % (self.team_a, self.points_a, self.points_b, self.team_b)

    class Meta:
        verbose_name_plural = "matches"
