import re
import os
import json
import pandas as pd

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_principal import (Permission, Principal, RoleNeed)
from flask_uploads import (UploadSet, DOCUMENTS)
from sqlalchemy import func, or_, and_

bcrypt = Bcrypt()
login_manager = LoginManager()
principal = Principal()

login_manager.login_view = "user_bp.login"
login_manager.session_protection = "strong"
login_manager.login_message = ''
login_manager.login_message_category = 'info'

# 权限
admin_permission = Permission(RoleNeed('admin'))  # 添加权限 与manage 对应
default_permission = Permission(RoleNeed('default'))

# upload
file_result = UploadSet('fileresult', DOCUMENTS)


@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(user_id)


class ResultToSql(object):

    def __init__(self, file):
        self.file = file
        self.df_dict = pd.read_excel(self.file, sheet_name=None, keep_default_na=False)

    def df_to_dic(self, df, sta=None):
        result_dict = {}
        if sta:
            for sam in df.columns:
                row_dict = {}
                for i in df.index:
                    row_dict[i] = df.loc[i][sam]
                result_dict[sam] = row_dict
        else:
            for i in df.index:
                row_dict = {}
                for sam in df.columns:
                    row_dict[sam] = df.loc[i][sam]
                result_dict[i] = row_dict
        return result_dict

    def result_dic(self, item='snv'):
        for name, df in self.df_dict.items():
            if name == item:
                if item == 'stat':
                    data = df[df.columns[-2:]].values
                    index = df.index
                    columns = df.columns[-2:]
                    df_stat = pd.DataFrame(data=data, index=index, columns=columns)
                    dict_df = self.df_to_dic(df_stat, 'stat')
                else:
                    dict_df = self.df_to_dic(df)
                return dict_df


def get_name(item):
    pat = '(\[.*\].)(.*)'
    m = re.match(pat, item)
    if m:
        name = (m.group(2))
    else:
        name = item
    name = (re.sub('#.', '', name))
    num = re.search('^\d', name)
    if num:
        name = re.sub('^\d', '_{}'.format(num.group()), name)
    name = name.replace('%', '')
    name = name.replace(':', '')
    name = name.replace('.', '')
    name = name.replace('该点在不同测序平台/tuomor/normal出现次数。','history')
    name = name.strip(')')
    name = (re.sub('.?\(', ' ', name))
    name = name.replace(' >', '')
    name = '_'.join(name.split(' '))
    return name


def dict_to_json(res, file_json):
    dic_re = {}
    # print(res.result_dic('stat'))  'germline_total','germline_filter',
    for item in ['stat', 'snv', 'cnv', 'sv_no', 'germline_total', 'germline_filter', '化疗']:
        dic_s = {}
        dic = res.result_dic(item)
        if dic:
            if item == 'stat':
                for key in dic.keys():
                    dic_s[key] = dic[key]['Q30']
            else:
                dic_s['total'] = len(dic.keys())
        else:
            dic_s['total'] = '无'
        item = item.replace('化疗', 'chem')
        dic_re[item] = dic_s
    json_str = json.dumps(dic_re, indent=4)
    with open(file_json, 'w')as f:
        f.write(json_str)


class SaveInSql(object):

    def create_stat(self, res, dic_v):
        res.Tag = str(dic_v["Q30"])
        res.Raw_Reads_All_reads = float(dic_v["[Total] Raw Reads (All reads)"])
        res.Raw_Dat_Mb = float(dic_v["[Total] Raw Data(Mb)"])
        res.Q30 = float(dic_v["Q30"])
        res.Fraction_of_Mapped_Reads = float(dic_v["[Total] Fraction of Mapped Reads"])
        res.Fraction_of_PCR_duplicate_reads = float(dic_v["[Total] Fraction of PCR duplicate reads"])
        res.Fraction_of_Target_Reads_in_mapped_reads = float(dic_v["[Target] Fraction of Target Reads in mapped reads"])
        res.Fraction_of_Target_Data_in_mapped_data = float(dic_v["[Target] Fraction of Target Data in mapped data"])
        res.Average_depth = float(dic_v["[Target] Average depth"])
        res.Average_dept_rmdup = float(dic_v["[Target] Average depth(rmdup)"])
        res.Fraction_Region_covered_0_AD = float(dic_v["[Target] Fraction Region covered > 0% AD"])
        res.Fraction_Region_covered_5_AD = float(dic_v["[Target] Fraction Region covered > 5% AD"])
        res.Fraction_Region_covered_10_AD = float(dic_v["[Target] Fraction Region covered > 10% AD"])
        res.Fraction_Region_covered_20_AD = float(dic_v["[Target] Fraction Region covered > 20% AD"])
        res.Fraction_Region_covered_30_AD = float(dic_v["[Target] Fraction Region covered > 30% AD"])
        res.Fraction_Region_covered_40_AD = float(dic_v["[Target] Fraction Region covered > 40% AD"])
        res.Fraction_Region_covered_50_AD = float(dic_v["[Target] Fraction Region covered > 50% AD"])
        res.Fraction_Region_covered_60_AD = float(dic_v["[Target] Fraction Region covered > 60% AD"])
        res.Fraction_Region_covered_70_AD = float(dic_v["[Target] Fraction Region covered > 70% AD"])
        res.Fraction_Region_covered_80_AD = float(dic_v["[Target] Fraction Region covered > 80% AD"])
        res.Fraction_Region_covered_90_AD = float(dic_v["[Target] Fraction Region covered > 90% AD"])
        res.Fraction_Region_covered_100_AD = float(dic_v["[Target] Fraction Region covered > 100% AD"])
        res.Fraction_Region_covered_150_AD = float(dic_v["[Target] Fraction Region covered > 150% AD"])
        res.Fraction_Region_covered_200_AD = float(dic_v["[Target] Fraction Region covered > 200% AD"])
        res.Fraction_Region_covered_300_AD = float(dic_v["[Target] Fraction Region covered > 300% AD"])
        res.Fraction_Region_covered_350_AD = float(dic_v["[Target] Fraction Region covered > 350% AD"])
        res.Fraction_Region_covered_400_AD = float(dic_v["[Target] Fraction Region covered > 400% AD"])

    def create_snv(self, res, dic_v):
        res.Tag = str(dic_v["c.HGVS"])
        res.Chr = str(dic_v["Chr"])
        res.Start = str(dic_v["Start"])
        res.End = str(dic_v["End"])
        res.Ref = str(dic_v["Ref"])
        res.Alt = str(dic_v["Alt"])
        res.FuncrefGene = str(dic_v["Func.refGene"])
        res.GenerefGene = str(dic_v["Gene.refGene"])
        res.GeneDetailrefGene = str(dic_v["GeneDetail.refGene"])
        res.ExonicFuncrefGene = str(dic_v["ExonicFunc.refGene"])
        res.AAChangerefGene = str(dic_v["AAChange.refGene"])
        res.InterVa_automated = str(dic_v["InterVar(automated)"])
        res.CIViC = str(dic_v["CIViC"])
        res.OncoKB = str(dic_v["OncoKB"])
        res.CKB = str(dic_v["CKB"])
        res.Clinvar = str(dic_v["Clinvar"])
        res.COSMIC = str(dic_v["COSMIC"])
        res.cosmic_combine = str(dic_v["cosmic_combine"])
        res.CLINSIG = str(dic_v["CLINSIG"])
        res.CLNDBN = str(dic_v["CLNDBN"])
        res.CLNACC = str(dic_v["CLNACC"])
        res.CLNDSDB = str(dic_v["CLNDSDB"])
        res.CLNDSDBID = str(dic_v["CLNDSDBID"])
        res.avsnp147 = str(dic_v["avsnp147"])
        res.snp138 = str(dic_v["snp138"])
        res.ExAC_nonpsych_EAS = str(dic_v["ExAC_nonpsych_EAS"])
        res.gnomAD_exome_EAS = str(dic_v["gnomAD_exome_EAS"])
        res.gnomAD_genome_ALL = str(dic_v["gnomAD_genome_ALL"])
        res.gnomAD_genome_EAS = str(dic_v["gnomAD_genome_EAS"])
        res._1000g2015aug_eas = str(dic_v["1000g2015aug_eas"])
        res.esp6500siv2_all = str(dic_v["esp6500siv2_all"])
        res.dbscSNV_ADA_SCORE = str(dic_v["dbscSNV_ADA_SCORE"])
        res.dbscSNV_RF_SCORE = str(dic_v["dbscSNV_RF_SCORE"])
        res.REVEL = str(dic_v["REVEL"])
        res.SIFT_pred = str(dic_v["SIFT_pred"])
        res.Polyphen2_HDIV_pred = str(dic_v["Polyphen2_HDIV_pred"])
        res.FATHMM_pred = str(dic_v["FATHMM_pred"])
        res.Otherinfo = str(dic_v["Otherinfo"])
        res.cHGVS = str(dic_v["c.HGVS"])
        res.pHGVS = str(dic_v["p.HGVS"])
        res._575_Transcript = str(dic_v["575_Transcript"])
        res.exon = str(dic_v["exon"])
        res.total_depth = str(dic_v["total depth"])
        res.germline_risk = str(dic_v["germline risk"])
        res.normal_af = str(dic_v["normal_af"])
        res.normal_dp = str(dic_v["normal_dp"])
        res.tumor_af = str(dic_v["tumor_af"])
        res.tumor_dp = str(dic_v["tumor_dp"])
        res.history = str(dic_v['历史出现次数'])

    def create_cnv(self, res, dic_v):
        res.Tag = str(dic_v["gene"])
        res.chromosome = str(dic_v["chromosome"])
        res.start = str(dic_v["start"])
        res.end = str(dic_v["end"])
        res.gene = str(dic_v["gene"])
        res.depth = str(dic_v["depth"])
        res.copy_number = str(dic_v["copy_number"])

    def create_sv_no(self, res, dic_v):
        res.Tag = str(dic_v["one start"])
        res.sample = str(dic_v["sample"])
        res.fusion_one = str(dic_v["fusion_one"])
        res.gene_name = str(dic_v["gene_name"])
        res.reads_count = str(dic_v["reads count"])
        res.one_chromosome = str(dic_v["one chromosome"])
        res.one_start = str(dic_v["one start"])
        res.two_chromosome = str(dic_v["two chromosome"])
        res.map_start = str(dic_v["map start"])
        res.gene_region = str(dic_v["gene region"])
        res.频率 = str(dic_v["频率"])
        res.分子模板数 = str(dic_v["分子模板数"])

    def create_germline_total(self, res, dic_v):
        res.locus = str(dic_v["# locus"])
        res.type = str(dic_v["type"])
        res.ref = str(dic_v["ref"])
        res.length = str(dic_v["length"])
        res.genotype = str(dic_v["genotype"])
        res.filter = str(dic_v["filter"])
        res.pvalue = str(dic_v["pvalue"])
        res.coverage = str(dic_v["coverage"])
        res.allele_coverage = str(dic_v["allele_coverage"])
        res.maf = str(dic_v["maf"])
        res.gene = str(dic_v["gene"])
        res.transcript = str(dic_v["transcript"])
        res.location = str(dic_v["location"])
        res.function = str(dic_v["function"])
        res.codon = str(dic_v["codon"])
        res.exon = str(dic_v["exon"])
        res.protein = str(dic_v["protein"])
        res.coding = str(dic_v["coding"])
        res.sift = str(dic_v["sift"])
        res.polyphen = str(dic_v["polyphen"])
        res.grantham = str(dic_v["grantham"])
        res.normalizedAlt = str(dic_v["normalizedAlt"])
        res._5000Exomes = str(dic_v["5000Exomes"])
        res.FATHMM = str(dic_v["FATHMM"])
        res.NamedVariants = str(dic_v["NamedVariants"])
        res.clinvar = str(dic_v["clinvar"])
        res.cosmic = str(dic_v["cosmic"])
        res.dbsnp = str(dic_v["dbsnp"])
        res.dgv = str(dic_v["dgv"])
        res.dra = str(dic_v["dra"])
        res.drugbank = str(dic_v["drugbank"])
        res.exac = str(dic_v["exac"])
        res.go = str(dic_v["go"])
        res.omim = str(dic_v["omim"])
        res.pfam = str(dic_v["pfam"])
        res.phylop = str(dic_v["phylop"])
        res.MyVariantDefaultDb_hg19 = str(dic_v["MyVariantDefaultDb_hg19"])

    def create_germline_filter(self, res, dic_v):
        res.locus = str(dic_v["# locus"])
        res.type = str(dic_v["type"])
        res.ref = str(dic_v["ref"])
        res.length = str(dic_v["length"])
        res.genotype = str(dic_v["genotype"])
        res.filter = str(dic_v["filter"])
        res.pvalue = str(dic_v["pvalue"])
        res.coverage = str(dic_v["coverage"])
        res.allele_coverage = str(dic_v["allele_coverage"])
        res.maf = str(dic_v["maf"])
        res.gene = str(dic_v["gene"])
        res.transcript = str(dic_v["transcript"])
        res.location = str(dic_v["location"])
        res.function = str(dic_v["function"])
        res.codon = str(dic_v["codon"])
        res.exon = str(dic_v["exon"])
        res.protein = str(dic_v["protein"])
        res.coding = str(dic_v["coding"])
        res.sift = str(dic_v["sift"])
        res.polyphen = str(dic_v["polyphen"])
        res.grantham = str(dic_v["grantham"])
        res.normalizedAlt = str(dic_v["normalizedAlt"])
        res._5000Exomes = str(dic_v["5000Exomes"])
        res.FATHMM = str(dic_v["FATHMM"])
        res.NamedVariants = str(dic_v["NamedVariants"])
        res.clinvar = str(dic_v["clinvar"])
        res.cosmic = str(dic_v["cosmic"])
        res.dbsnp = str(dic_v["dbsnp"])
        res.dgv = str(dic_v["dgv"])
        res.dra = str(dic_v["dra"])
        res.drugbank = str(dic_v["drugbank"])
        res.exac = str(dic_v["exac"])
        res.go = str(dic_v["go"])
        res.omim = str(dic_v["omim"])
        res.pfam = str(dic_v["pfam"])
        res.phylop = str(dic_v["phylop"])
        res.MyVariantDefaultDb_hg19 = str(dic_v["MyVariantDefaultDb_hg19"])

    def create_chem(self, res, dic_v):
        res.Tag = str(dic_v["pos"])
        res.chro = str(dic_v["chro"])
        res.pos = str(dic_v["pos"])
        res.total_cov = str(dic_v["total_cov"])
        res.ref_cov = str(dic_v["ref_cov"])
        res.dep_detail = str(dic_v["dep_detail"])
        res.ref_af = str(dic_v["ref_af"])
        res.genotype = str(dic_v["genotype"])


def save_in_sql(class_name, resul, filename, session):
    sav = SaveInSql()
    func_name = [sav.create_stat, sav.create_snv, sav.create_cnv, sav.create_chem]
    for item_c, item_f in zip(class_name, func_name):
        item = item_c.__name__.lower()
        item = item.replace('chem', '化疗')
        s = resul.result_dic(item)
        print(item)
        sam_name = filename.split('.')[0]
        if s:
            for k in s.keys():
                if item == 'stat':
                    sam_name = k
                res = item_c(Sample_name=sam_name)
                dic_v = s[k]
                item_f(res, dic_v)
                # if item_c.query.filter(and_(item_c.Sample_name==sam_name),item_c.Tag=='').first():
                #     pass
                # else:
                session.add(res)
                session.commit()


def dict_to_sql(res, item_c, session):
    dic_re = {}
    # print(res.result_dic('stat'))  'germline_total','germline_filter',
    for item in ['stat', 'snv', 'cnv', 'sv_no', 'germline_total', 'germline_filter', '化疗']:
        dic = res.result_dic(item)
        if dic:
            if item == 'stat':
                val = []
                for key in dic.keys():
                    val.append(dic[key]['Q30'])
            else:
                val = len(dic.keys())
                item = item.replace('化疗', 'chem')
        else:
            val = '无'
            item_c.item = '无'
        item = item.replace('化疗', 'chem')
        dic_re[item] = val
    print(dic_re)
    item_c.stat = '/'.join([str(i) for i in dic_re['stat']])
    item_c.snv = str(dic_re['snv'])
    item_c.cnv = str(dic_re['cnv'])
    item_c.sv_no = str(dic_re['sv_no'])
    item_c.germline_total = str(dic_re['germline_total'])
    item_c.germline_filter = str(dic_re['germline_filter'])
    item_c.chem = str(dic_re['chem'])
    item_c.status = '未审核'
    session.add(item_c)
    session.commit()


def export_to_excel(class_names,filename,filepath):
    writer = pd.ExcelWriter(os.path.join(os.getcwd(),filepath,'{}.xlsx'.format(filename)))
    for class_name in class_names:
        header = class_name.__table__.columns.keys()
        Ss = class_name.query.filter(class_name.Sample_name.startswith(filename)).all()
        dd = []
        for s in Ss:
            data = [getattr(s, key) for key in header]
            dd.append(data)
        df2 = pd.DataFrame(dd, columns=header)
        n_head = list(header)
        for item in header:
            if item in ['id', 'Tag']:
                n_head.remove(item)
        df3 = (df2[[i for i in n_head]]).copy()
        df3.to_excel(writer, sheet_name=class_name.__name__.lower(), index=False)
    writer.save()
    writer.close()
