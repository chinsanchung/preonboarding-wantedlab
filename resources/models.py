from database import db


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(), nullable=False)


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lang_tag = db.Column(db.String(100), nullable=False)


class CompanyName(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(
        db.Integer,
        db.ForeignKey("company.id", ondelete="CASCADE"),
    )
    company = db.relationship("Company", backref=db.backref("company_name"))
    lang_id = db.Column(
        db.Integer,
        db.ForeignKey("language.id"),
    )
    company_name = db.Column(db.String(200), nullable=False)


class CompanyTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(
        db.Integer,
        db.ForeignKey("company.id", ondelete="CASCADE"),
    )
    company = db.relationship("Company", backref=db.backref("tags"))
    lang_id = db.Column(
        db.Integer,
        db.ForeignKey("language.id"),
    )
    tag_name = db.Column(db.String(200), nullable=False)
