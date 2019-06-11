from flask_sqlalchemy import SQLAlchemy
from flask_login import AnonymousUserMixin

from app.extensions import bcrypt

db = SQLAlchemy()

roles = db.Table(
    'role_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255))
    passwd = db.Column(db.String(255))
    roles = db.relationship('Role', secondary=roles, backref=db.backref('users', lazy='dynamic'))



    def __init__(self, username):
        self.username = username
        default = Role.query.filter_by(name="default").one()
        self.roles.append(default)

    def __repr__(self):
        return "<User '{}'>".format(self.username)

    def set_password(self, password):
        self.passwd = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.passwd, password)

    @property
    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return str(self.id)


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class Stat(db.Model):
    __tablename__ = 'stat'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    Sample_name = db.Column(db.String(20))
    Tag = db.Column(db.String(20))
    Raw_Reads_All_reads = db.Column(db.Float())
    Raw_Dat_Mb = db.Column(db.Float())
    Q30 = db.Column(db.Float())
    Fraction_of_Mapped_Reads = db.Column(db.Float())
    Fraction_of_PCR_duplicate_reads = db.Column(db.Float())
    Fraction_of_Target_Reads_in_mapped_reads = db.Column(db.Float())
    Fraction_of_Target_Data_in_mapped_data = db.Column(db.Float())
    Average_depth = db.Column(db.Float())
    Average_dept_rmdup = db.Column(db.Float())
    Fraction_Region_covered_0_AD = db.Column(db.Float())
    Fraction_Region_covered_5_AD = db.Column(db.Float())
    Fraction_Region_covered_10_AD = db.Column(db.Float())
    Fraction_Region_covered_20_AD = db.Column(db.Float())
    Fraction_Region_covered_30_AD = db.Column(db.Float())
    Fraction_Region_covered_40_AD = db.Column(db.Float())
    Fraction_Region_covered_50_AD = db.Column(db.Float())
    Fraction_Region_covered_60_AD = db.Column(db.Float())
    Fraction_Region_covered_70_AD = db.Column(db.Float())
    Fraction_Region_covered_80_AD = db.Column(db.Float())
    Fraction_Region_covered_90_AD = db.Column(db.Float())
    Fraction_Region_covered_100_AD = db.Column(db.Float())
    Fraction_Region_covered_150_AD = db.Column(db.Float())
    Fraction_Region_covered_200_AD = db.Column(db.Float())
    Fraction_Region_covered_300_AD = db.Column(db.Float())
    Fraction_Region_covered_350_AD = db.Column(db.Float())
    Fraction_Region_covered_400_AD = db.Column(db.Float())


class Snv(db.Model):
    __tablename__ = 'snv'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    Sample_name = db.Column(db.String(20))
    Tag = db.Column(db.String(250))
    Chr = db.Column(db.String(50))
    Start = db.Column(db.String(50))
    End = db.Column(db.String(50))
    Ref = db.Column(db.String(200))
    Alt = db.Column(db.String(200))
    FuncrefGene = db.Column(db.String(50))
    GenerefGene = db.Column(db.String(50))
    GeneDetailrefGene = db.Column(db.String(500))
    ExonicFuncrefGene = db.Column(db.String(50))
    AAChangerefGene = db.Column(db.String(2000))
    InterVa_automated = db.Column(db.String(50))
    CIViC = db.Column(db.String(50))
    OncoKB = db.Column(db.String(50))
    CKB = db.Column(db.String(200))
    Clinvar = db.Column(db.String(250))
    COSMIC = db.Column(db.String(50))
    cosmic_combine = db.Column(db.String(250))
    CLINSIG = db.Column(db.String(500))
    CLNDBN = db.Column(db.String(500))
    CLNACC = db.Column(db.String(500))
    CLNDSDB = db.Column(db.String(500))
    CLNDSDBID = db.Column(db.String(500))
    avsnp147 = db.Column(db.String(50))
    snp138 = db.Column(db.String(50))
    ExAC_nonpsych_EAS = db.Column(db.String(50))
    gnomAD_exome_EAS = db.Column(db.String(50))
    gnomAD_genome_ALL = db.Column(db.String(50))
    gnomAD_genome_EAS = db.Column(db.String(50))
    _1000g2015aug_eas = db.Column(db.String(50))
    esp6500siv2_all = db.Column(db.String(50))
    dbscSNV_ADA_SCORE = db.Column(db.String(50))
    dbscSNV_RF_SCORE = db.Column(db.String(50))
    REVEL = db.Column(db.String(50))
    SIFT_pred = db.Column(db.String(50))
    Polyphen2_HDIV_pred = db.Column(db.String(50))
    FATHMM_pred = db.Column(db.String(50))
    Otherinfo = db.Column(db.String(50))
    cHGVS = db.Column(db.String(250))
    pHGVS = db.Column(db.String(50))
    _575_Transcript = db.Column(db.String(50))
    exon = db.Column(db.String(50))
    total_depth = db.Column(db.String(50))
    germline_risk = db.Column(db.String(50))
    normal_af = db.Column(db.String(50))
    normal_dp = db.Column(db.String(50))
    tumor_af = db.Column(db.String(50))
    tumor_dp = db.Column(db.String(50))
    status = db.Column(db.String(50))
    note = db.Column(db.String(50))
    history = db.Column(db.String(250))


class Cnv(db.Model):
    __tablename__ = 'cnv'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    Sample_name = db.Column(db.String(20))
    Tag = db.Column(db.String(50))
    chromosome = db.Column(db.String(50))
    start = db.Column(db.String(50))
    end = db.Column(db.String(50))
    gene = db.Column(db.String(50))
    depth = db.Column(db.String(50))
    copy_number = db.Column(db.String(50))


class Sv_no(db.Model):
    __tablename__ = 'sv_no'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    Sample_name = db.Column(db.String(20))
    Tag = db.Column(db.String(50))
    sample = db.Column(db.String(50))
    fusion_one = db.Column(db.String(50))
    gene_name = db.Column(db.String(50))
    reads_count = db.Column(db.String(50))
    one_chromosome = db.Column(db.String(50))
    one_start = db.Column(db.String(50))
    two_chromosome = db.Column(db.String(50))
    map_start = db.Column(db.String(50))
    gene_region = db.Column(db.String(50))
    频率 = db.Column(db.String(50))
    分子模板数 = db.Column(db.String(50))


class Germline_total(db.Model):
    __tablename__ = 'germline_total'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    Sample_name = db.Column(db.String(20))
    locus = db.Column(db.String(50))
    type = db.Column(db.String(50))
    ref = db.Column(db.String(50))
    length = db.Column(db.String(50))
    genotype = db.Column(db.String(50))
    filter = db.Column(db.String(50))
    pvalue = db.Column(db.String(50))
    coverage = db.Column(db.String(50))
    allele_coverage = db.Column(db.String(50))
    maf = db.Column(db.String(50))
    gene = db.Column(db.String(50))
    transcript = db.Column(db.String(50))
    location = db.Column(db.String(50))
    function = db.Column(db.String(50))
    codon = db.Column(db.String(50))
    exon = db.Column(db.String(50))
    protein = db.Column(db.String(50))
    coding = db.Column(db.String(50))
    sift = db.Column(db.String(50))
    polyphen = db.Column(db.String(50))
    grantham = db.Column(db.String(50))
    normalizedAlt = db.Column(db.String(50))
    _5000Exomes = db.Column(db.String(50))
    FATHMM = db.Column(db.String(50))
    NamedVariants = db.Column(db.String(50))
    clinvar = db.Column(db.String(50))
    cosmic = db.Column(db.String(50))
    dbsnp = db.Column(db.String(50))
    dgv = db.Column(db.String(50))
    dra = db.Column(db.String(50))
    drugbank = db.Column(db.String(50))
    exac = db.Column(db.String(50))
    go = db.Column(db.String(50))
    omim = db.Column(db.String(50))
    pfam = db.Column(db.String(50))
    phylop = db.Column(db.String(50))
    MyVariantDefaultDb_hg19 = db.Column(db.String(50))


class Germline_filter(db.Model):
    __tablename__ = 'germline_filter'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    Sample_name = db.Column(db.String(20))
    locus = db.Column(db.String(50))
    type = db.Column(db.String(50))
    ref = db.Column(db.String(50))
    length = db.Column(db.String(50))
    genotype = db.Column(db.String(50))
    filter = db.Column(db.String(50))
    pvalue = db.Column(db.String(50))
    coverage = db.Column(db.String(50))
    allele_coverage = db.Column(db.String(50))
    maf = db.Column(db.String(50))
    gene = db.Column(db.String(50))
    transcript = db.Column(db.String(50))
    location = db.Column(db.String(50))
    function = db.Column(db.String(50))
    codon = db.Column(db.String(50))
    exon = db.Column(db.String(50))
    protein = db.Column(db.String(50))
    coding = db.Column(db.String(50))
    sift = db.Column(db.String(50))
    polyphen = db.Column(db.String(50))
    grantham = db.Column(db.String(50))
    normalizedAlt = db.Column(db.String(50))
    _5000Exomes = db.Column(db.String(50))
    FATHMM = db.Column(db.String(50))
    NamedVariants = db.Column(db.String(50))
    clinvar = db.Column(db.String(50))
    cosmic = db.Column(db.String(50))
    dbsnp = db.Column(db.String(50))
    dgv = db.Column(db.String(50))
    dra = db.Column(db.String(50))
    drugbank = db.Column(db.String(50))
    exac = db.Column(db.String(50))
    go = db.Column(db.String(50))
    omim = db.Column(db.String(50))
    pfam = db.Column(db.String(50))
    phylop = db.Column(db.String(50))
    MyVariantDefaultDb_hg19 = db.Column(db.String(50))


class Chem(db.Model):
    __tablename__ = 'chem'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    Sample_name = db.Column(db.String(20))
    Tag = db.Column(db.String(50))
    chro = db.Column(db.String(50))
    pos = db.Column(db.String(50))
    total_cov = db.Column(db.String(50))
    ref_cov = db.Column(db.String(50))
    dep_detail = db.Column(db.String(50))
    ref_af = db.Column(db.String(50))
    genotype = db.Column(db.String(50))


class SampleStat(db.Model):
    __tablename__ = 'samplestat'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    Sample_name = db.Column(db.String(20))
    stat = db.Column(db.String(50))
    snv = db.Column(db.String(50))
    cnv = db.Column(db.String(50))
    sv_no = db.Column(db.String(50))
    germline_total = db.Column(db.String(50))
    germline_filter = db.Column(db.String(50))
    chem = db.Column(db.String(50))
    status = db.Column(db.String(50))