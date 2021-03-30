from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask import render_template, url_for, flash, redirect
# from forms import RegistrationForm, LoginForm

# woooooooooooohoooooo!
# https://stackoverflow.com/questions/57202736/where-should-i-implement-flask-custom-commands-cli
# import tests.bootstrap_tables as boot


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Supress deprecation message
db = SQLAlchemy(app)


@app.cli.command("initdb")
def reset_db():
    ''' Drops and Creates fresh database '''
    db.drop_all()
    db.create_all()
    print("Initialized clean DB tables")


@app.cli.command("bootstrap")
def bootstrap_data():
    ''' Populates database with some sample data '''
    db.drop_all()
    db.create_all()
    bootstrap_helper()
    print("Initialized and Bootstrapped DB tables with data")


# Association table: automatically updates based on Users and Projects tables
UserProjects = db.Table("userproject",
                        db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
                        db.Column("project_id", db.Integer, db.ForeignKey("project.id"), primary_key=True))


class Users(db.Model):
    ''' Users Table:
    User profile information and Fact table (collection of many foreign keys)
    '''
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_image = db.Column(db.String(20), nullable=False, default="profile.jpg")
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_moderator = db.Column(db.Boolean, default=False, nullable=False)
    skill_proficiency_1 = db.Column(db.Integer, nullable=False)
    skill_proficiency_2 = db.Column(db.Integer, nullable=False)
    skill_proficiency_3 = db.Column(db.Integer, nullable=False)

    # option 1) 1 to Many
    # Multiple foriegn keys to one table
    skill_id_1 = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    skill_id_2 = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    skill_id_3 = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    skill_1 = db.relationship("Skills", foreign_keys=skill_id_1)
    skill_2 = db.relationship("Skills", foreign_keys=skill_id_2)
    skill_3 = db.relationship("Skills", foreign_keys=skill_id_3)
    # option 2) Many to Many
    # secondary join to reduce the need for 3 columns for each skill
    # need to make an association table ("users_skills")
    # skills = db.relationship("Skills", secondary=users_skills, backref="users", lazy="select")

    def __repr__(self):
        return f"User('{self.first_name}', '{self.last_name}', '{self.email}')"


class Projects(db.Model):
    ''' Projects Table: 
    containg group projects a user can post
    '''
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(250), unique=True, nullable=False)
    desc = db.Column(db.String(500), unique=False, nullable=False)
    creation_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    start_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    target_end_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    # https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many
    project_members = db.relationship('Users',
                                      secondary=UserProjects,
                                      lazy='subquery',
                                      backref="user_projects")

    def __repr__(self):
        return f"Project[ID:'{self.id}', Name:'{self.name}'] "


class Skills(db.Model):
    ''' Skills Table:
    Common technical skills per StackOverflow 2019 survey
    '''
    __tablename__ = 'skill'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    desc = db.Column(db.String(250), nullable=False)
    image = db.Column(db.String(20), nullable=False, default="skill.jpg")

    # Relationship on skills, defines users per skill
    # ---------------------- Class name here -- some useful name for Skills.<backref>
    # users = db.relationship("Users", backref="allskills", lazy='dynamic',
    #                         primaryjoin="and_(Skills.id==Users.skill_id_1, Skills.id==Users.skill_id_2, Skills.id==Users.skill_id_3)")

    def __repr__(self):
        return f"Skill('{self.name}', '{self.desc}')"


class csField(db.Model):
    ''' csField Table:
    Common SWE related roled per StackOverflow 2019 survey
    - examples of csfield_name {backend, frontend, mobile ,devops, etc.}
    '''
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    desc = db.Column(db.String(250), nullable=False)
    image = db.Column(db.String(20), nullable=False, default="csField.jpg")


class ProjectInterests(db.Model):
    ''' Interests Table:
    Types of projects a user has preference in, for example -
    - Industries (ex. Aerospace, Finance, IoT, etc.)
    - General interests in technology (ex. Machine Learning, NLP, Autonomous vehicles)
    '''
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    desc = db.Column(db.String(250), nullable=False)
    image = db.Column(db.String(20), nullable=False, default="ProjectInterests.jpg")

# ----------------------------------------------------------------------------------------------------------------------------


def bootstrap_helper():
    ''' Actually populates database with data '''
    # Add Skills
    # --------------------------------------------------------------
    skill_python = Skills(name="Python", desc="An general purpose Object Oriented language")
    skill_cpp = Skills(name="C++", desc="Low Level Programming Language")
    skill_3 = Skills(name="Javascript", desc="Web Development Language")
    skill_4 = Skills(name="Koitlin", desc="Mobile development")

    db.session.add(skill_python)
    db.session.add(skill_cpp)
    db.session.add(skill_3)
    db.session.add(skill_4)
    db.session.commit()

    # Add Users
    # --------------------------------------------------------------

    user_1 = Users(first_name='daniel', last_name='bae', email="dan@gmail.com",
                   skill_id_1=skill_python.id,
                   skill_proficiency_1=4,
                   skill_id_2=skill_cpp.id,
                   skill_proficiency_2=3,
                   skill_id_3=skill_3.id,
                   skill_proficiency_3=2
                   )
    user_2 = Users(first_name='simon', last_name='says', email="jeff@gmail.com",
                   skill_id_1=skill_cpp.id,
                   skill_proficiency_1=3,
                   skill_id_2=skill_python.id,
                   skill_proficiency_2=4,
                   skill_id_3=skill_4.id,
                   skill_proficiency_3=2
                   )
    user_3 = Users(first_name='jeff', last_name='williams', email="jw@gmail.com",
                   skill_id_1=skill_4.id,
                   skill_proficiency_1=3,
                   skill_id_2=skill_3.id,
                   skill_proficiency_2=4,
                   skill_id_3=skill_cpp.id,
                   skill_proficiency_3=2
                   )
    db.session.add(user_1)
    db.session.add(user_2)
    db.session.add(user_3)
    db.session.commit()

    # Add Projects
    # --------------------------------------------------------------
    project_1 = Projects(name="Lets make a React App!!!",
                         desc="Welcome all levels of exp, just looking to get expossure to react")
    project_2 = Projects(name="Anyone looking to get started with mobile development?",
                         desc="Currently interested in Koitlin dev, but open to other stacks as well!")
    db.session.add(project_1)
    db.session.add(project_2)

    # Projects - Adding members to projects
    # --------------------------------------------------------------
    # Adding new rows using pythonic lists functionality (append, extend)
    project_1.project_members.extend((user_1, user_2, user_3))
    project_2.project_members.append(user_3)
    db.session.commit()

    # Add Fields
    # --------------------------------------------------------------
    field_1 = csField(name="Front-End", desc="User interface")
    field_2 = csField(name="Back-End", desc="Servers")
    db.session.add(field_1)
    db.session.add(field_2)
    db.session.commit()

    # Add ProjectInterests
    # --------------------------------------------------------------
    interest_1 = ProjectInterests(name="Medical", desc="Genteics, Medical imaging, etc.")
    interest_2 = ProjectInterests(name="Space", desc="Simulations, Robotics, Computer vision")
    db.session.add(interest_1)
    db.session.add(interest_2)
    db.session.commit()


# Sample Route
@ app.route('/')
@ app.route('/home')
def home():
    return "hello"


if __name__ == '__main__':
    app.run(debug=True)
