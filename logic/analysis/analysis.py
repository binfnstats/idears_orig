#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 16:39:52 2021

@author: michaelallwright

This file contains a set of functions that are to be used in the new version of UKB
to do the key analyses

"""

#key information to run financial passport for - user and start/end date. Move to config file?

import pandas as pd
import numpy as np
from datetime import datetime

import seaborn as sns
import os
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
from decimal import Decimal

from scipy import stats
from scipy.stats import t
from sklearn.preprocessing import StandardScaler
from logic.ml.classification_shap import IDEARs_funcs

ml=IDEARs_funcs()



class AnalysisCharts(object):
	"""
	Incexp Model for affordability.
	"""

	def __init__(self):
		"""
		Initilising models.
		"""

		self.date_run=str(datetime.now().date())
		self.path="/Users/michaelallwright/Dropbox (Sydney Uni)/michael_PhD/Projects/UKB/Data/"
		self.pathfig='/Users/michaelallwright/Documents/GitHub/UKB/PD/figures/'
		self.path_figures_dem= "/Users/michaelallwright/Documents/GitHub/UKB/dementia/figures/"
		self.path_figures_pd= "/Users/michaelallwright/Documents/GitHub/UKB/PD/figures/"
		self.path_figures_pain= "/Users/michaelallwright/Documents/GitHub/UKB/Pain/figures/"
		self.date_run=str(datetime.now().date())

		#check which cholesterol it is
		self.yaxis_units=dict({'igf1_f30770_0_0':'nmol/L','total_bilirubin_f30840_0_0':'umol/L',
			'AST_ALT_ratio':'AST:ALT ratio',
			'creatinine_enzymatic_in_urine_f30510_0_0':'micromole/L',
			'urate_f30880_0_0':'umol/L',
			'neutrophill_count_f30140_0_0':'10^9 cells/Litre','lymphocyte_count_f30120_0_0':'10^9 cells/Litre',
			'neutrophill_lymphocyte_ratio':'Ratio',
		 'creactive_protein_f30710_0_0':'mg/L','ibuprofen':'Percentage taking Ibuprofen',
		 'cholesterol_f30690_0_0':'mmol/l','hdl_cholesterol_f30760_0_0':'mmol/l',
		 'waist_circumference_f48_0_0':'cm','ldl_direct_f30780_0_0':'mmol/L',
		 'Total ICD10 Conditions at baseline':'',
		 'number_of_treatmentsmedications_taken_f137_0_0':'',
		 'hand_grip_strength_left_f46_0_0':'Kg', 'hand_grip_strength_right_f47_0_0':'Kg',
		 'usual_walking_pace_f924_0_0':'Interview speed',
		   'forced_vital_capacity_fvc_f3062_0_0':'Litres',
		   'glycated_haemoglobin_hba1c_f30750_0_0':'nmol/L'})
		


	def findcols(self,df,string):
		return [col for col in df if string in col]
	
	def df_quint(self,df,var='perc_correct_matches_rounds'):
		if df[var].nunique()>5:
			df[var+'_quint']=pd.qcut(df[var],5,labels=False,duplicates='drop').astype(int)+1
		else:
			print('insufficient variable values')
		return df

	def pop_char_dem_func(self,df,depvar='dementia'):
		
		mask_m=(df['sex_f31_0_0']==0)
		maska0=(df['APOE4_Carriers']==0)
		maska1=(df['APOE4_Carriers']==1)
		maska2=(df['APOE4_Carriers']==2)

		n=df.shape[0]
		age=str(round(df['age_when_attended_assessment_centre_f21003_0_0'].mean(),2))+'+/-'+\
	str(round(df['age_when_attended_assessment_centre_f21003_0_0'].std(),2))
		males=str(df[mask_m].shape[0])+' ('+str(round(df[mask_m].shape[0]/df.shape[0],2))+')'
		females=str(df[~mask_m].shape[0])+' ('+str(round(df[~mask_m].shape[0]/df.shape[0],2))+')'
		apoe0=str(df[maska0].shape[0])+' ('+str(round(df[~maska0].shape[0]/df.shape[0],2))+')'
		apoe1=str(df[maska1].shape[0])+' ('+str(round(df[~maska1].shape[0]/df.shape[0],2))+')'
		apoe2=str(df[maska2].shape[0])+' ('+str(round(df[~maska2].shape[0]/df.shape[0],2))+')'

		return n,age,males,females,apoe0,apoe1,apoe2

	def pop_char_dem(self,df,depvar='dementia'):
		vars=['n','Age at baseline (years)','Males','Females','APOE4 (0 alleles)','APOE4 (1 allele)','APOE4 (2 alleles)']
		mask_case=(df[depvar]==1)
		cases=self.pop_char_dem_func(df[mask_case])
		controls=self.pop_char_dem_func(df[~mask_case])
		total=self.pop_char_dem_func(df)

		df_sum=pd.DataFrame({'Variable':vars,'Cases':cases,'Controls':controls,'Total':total})

		return df_sum

	def agenorm(self,df,var,normvar='age_when_attended_assessment_centre_f21003_0_0'):

		df2=df.loc[pd.notnull(df[var])&(df[var]!=np.inf)]
		df_sum=pd.DataFrame(df2.groupby([normvar]).agg({var:['mean']})).reset_index()
		df_sum.columns=[normvar,'mean'+var]

		df=pd.merge(df,df_sum,on=normvar,how='left')

		df[var]=df[var].mean()*df[var]/df['mean'+var]
		df.drop(columns=['mean'+var],inplace=True)
		return df

	def varnorm(self,df,var,normvar=['age_when_attended_assessment_centre_f21003_0_0']):
		df_sum=pd.DataFrame(df.groupby(normvar).agg({var:['mean']})).reset_index()
		df_sum.columns=normvar+['mean'+var]

		df=pd.merge(df,df_sum,on=normvar,how='left')

		df[var]=df[var].mean()*df[var]/df['mean'+var]
		df.drop(columns=['mean'+var],inplace=True)
		return df




	def agenorm2(self,df,var):
		df_sum=pd.DataFrame(df.groupby(['age_when_attended_assessment_centre_f21003_0_0']).agg({var:['mean']})).reset_index()
		df_sum.columns=['age_when_attended_assessment_centre_f21003_0_0','mean'+var]

		df=pd.merge(df,df_sum,on='age_when_attended_assessment_centre_f21003_0_0',how='left')
		df[var]=df[var]/df['mean'+var]
		df.drop(columns=['mean'+var],inplace=True)
		return df

	def gend_norm(self,df,var):
		df_sum=pd.DataFrame(df.groupby(['sex_f31_0_0']).\
	agg({var:['mean']})).reset_index()
		df_sum.columns=['sex_f31_0_0','mean'+var]

		df=pd.merge(df,df_sum,on=['sex_f31_0_0'],how='left')
		df[var]=df[var]/df['mean'+var]
		df.drop(columns=['mean'+var],inplace=True)
		return df

	def gend_norm2(self,df,vars):
		df_sum=pd.DataFrame(df.groupby(['sex_f31_0_0'])[vars].mean()).reset_index()
		df_sum.columns=['sex_f31_0_0']+['mean'+v for v in vars]

		df=pd.merge(df,df_sum,on=['sex_f31_0_0'],how='left')
		df[vars]=df[vars]/df[['mean'+ v for v in vars]]
		df.drop(columns=['mean'+v for v in vars],inplace=True)
		return df

	def age_gend_norm2(self,df,var):
		df_sum=pd.DataFrame(df.groupby(['age_when_attended_assessment_centre_f21003_0_0','sex_f31_0_0']).\
	agg({var:['mean']})).reset_index()
		df_sum.columns=['age_when_attended_assessment_centre_f21003_0_0','sex_f31_0_0','mean'+var]

		df=pd.merge(df,df_sum,on=['age_when_attended_assessment_centre_f21003_0_0','sex_f31_0_0'],how='left')
		df[var]=df[var]/df['mean'+var]
		df.drop(columns=['mean'+var],inplace=True)
		return df

	def age_gend_norm_mult(self,df,vars,normvars=['age_when_attended_assessment_centre_f21003_0_0','sex_f31_0_0']):
		df_sum=pd.DataFrame(df.groupby(normvars)[vars].mean()).reset_index()
   
		df_sum.columns=normvars+['mean'+v for v in vars]

		df=pd.merge(df,df_sum,on=normvars,how='left')

		for v in vars:
			df[v]=df[v]/df['mean'+v]
		df.drop(columns=['mean'+v for v in vars],inplace=True)
		return df

		
	def std_scale(self,df,vars=[]):
		for var in vars:
			trans = StandardScaler()
			df[var+'std']=trans.fit_transform(np.asarray(df[var]).reshape(-1, 1))
		return df

	def std_scale_newvar(self,df,vars=[],name='inflammation'):
		for var in vars:
			trans = StandardScaler()
			df[var+'std']=trans.fit_transform(np.asarray(df[var]).reshape(-1, 1))
		
		df[name]=df[[v+'std' for v in vars]].sum(axis=1)
		df.drop(columns=[v+'std' for v in vars],inplace=True)
		return df




	def slope(self,df,var,depvar):
	
		mask_aspnnull=(pd.notnull(df[var]))
		trans = StandardScaler()
		df[var+'_std']=trans.fit_transform(np.asarray(df[var]).reshape(-1, 1))
		
		slope_ap, intercept_ap, r_value_ap, p_value_ap, std_err_ap = \
		stats.linregress(df[mask_aspnnull][var+'_std'],df[mask_aspnnull][depvar])
		
		slope_ap=slope_ap
		
		return slope_ap, intercept_ap, r_value_ap, p_value_ap, std_err_ap

	def calc_rr(self,df,var,path,slicevar='APOE4 Status',splitval=0,depvar='dementia',
		xlabel='Total number of conditions at baseline',ylabel='Relative Risk',leg=0,quint=1,val_comp=1,figname='fig3_',quant=1,
		vcomp='RR',pic_ext='.svg'):

		df=df.loc[pd.notnull(df[var]),]
		df.loc[df[var]==np.inf,var]=np.nan

		var_orig=var

		if quint==1:
			df=self.df_quint(df,var=var)
			var=var+'_quint'

		df1=df.copy()
		

		if quant<1:
			df1=df1.loc[df[var]<df1[var].quantile(quant),]

		df_sum=pd.DataFrame(df1.groupby([slicevar,var]).agg({depvar:['sum','count']})).reset_index()
		df_sum.columns=[slicevar,var,depvar+'_sum',depvar+'_count']
		df_sum['UI']=df_sum[slicevar].astype(str)+'_'+df_sum[var].astype(str)
		df_sum['ART']=df_sum[depvar+'_sum']/df_sum[depvar+'_count']
		
		df_sum['ARC']=0
		df_sum['RR']=0
		
		#keep original df here for whole area
		slope_diff,pval=self.pvalue_slopes(df,var=var_orig,depvar=depvar,splitvar=slicevar,splitval=splitval,val_comp=val_comp)
		
		df2=df1.copy()

		if slicevar=='APOE4_Status':
			df2.loc[df2[slicevar]==0,slicevar]='APOE4 -ve'
			df2.loc[df2[slicevar]==1,slicevar]='APOE4 +ve'

		for q in df_sum['UI'].unique():
			mask=(df_sum['UI']==q)
			ARC=df_sum[~mask][depvar+'_sum'].sum()/df_sum[~mask][depvar+'_count'].sum()
			df_sum['ARC'][mask]=ARC
			df_sum['RR']=df_sum['ART']/df_sum['ARC']
			
		df_sum2=pd.DataFrame(df_sum.groupby([slicevar,var])['RR'].mean().unstack(slicevar)).reset_index()
		figure(figsize=(15, 10))
		
		if vcomp=='RR':
			ax=sns.lineplot(data=df_sum, x=var, y='RR',hue=slicevar,estimator='mean',palette = 'Greys_r',linewidth = 4)#,palette = Greys_r)
		elif vcomp=='ART':
			ax=sns.lineplot(data=df2, x=var, y=depvar,hue=slicevar,estimator='mean',palette = 'Greys_r',linewidth = 4)
		ax.set(xlabel=xlabel,ylabel=ylabel)

		
		handles, labels = ax.get_legend_handles_labels()
		ax.legend(handles=handles[2:], labels=labels[2:])
		print(handles)
		
		plt.setp(ax.get_legend().get_texts(), fontsize='32') # for legend text
		
		if leg==0:	
			ax.get_legend().remove()

		plt.xticks(fontsize='32')
		plt.yticks(fontsize='32')

		if 'longstanding' in var:
			ax.xaxis.set_ticks(np.arange(3))
		if quint==1:
			ax.xaxis.set_ticks(np.arange(5))
		if 'Retired' in var:
			ax.xaxis.set_ticks(np.arange(2))
		if 'overall_health_rating_f2178_0_0' in var:
			ax.xaxis.set_ticks(np.arange(3))
		if 'alcohol' in var:
			ax.xaxis.set_ticks(np.arange(5))

		if vcomp=='ART':
			ax.yaxis.set_ticks(np.arange(7)*0.005)

		if quint==1:
			ax.xaxis.set_ticks(np.arange(5)+1)

		
		
		plt.xlabel(xlabel, fontsize=32)
		plt.ylabel(ylabel, fontsize=26)

		#plt.ylim(10, 40)
		if pval<0.001:
			symb="(***)"
		elif pval<0.01:
			symb="(**)"
		elif pval<0.05:
			symb="(*)"
		else:
			symb="(ns)"
		if round(pval,4)==0:
			valsymb="{:.2E}".format(Decimal(pval))
		else:
			valsymb=str(round(pval,5))
			
		
			
		plt.text(0.5,0.7,'slope ratio: '+str("{:.0%}".format(round(slope_diff,5))+' '+str(symb)),horizontalalignment='center',
			verticalalignment='center', transform = ax.transAxes, fontsize='34')

		#plt.text(0.5,0.7,str(round(slope_diff,2))+' '+str(symb),horizontalalignment='center',
		#	verticalalignment='center', transform = ax.transAxes, fontsize='28')
		
		plt.savefig(path+figname+"_"+var+"_"+self.date_run+pic_ext, dpi=300)
		plt.show()

		# return the variable summarised by its groups and values
		df_out=pd.DataFrame(df2.groupby([var,slicevar]).agg({depvar:['mean','sum','count']})).reset_index()
		
		df_out.columns=['Variable_value',slicevar,depvar+' incidence rate','total '+depvar,'total participants']

		if quint==1:
			suff=' (quintile)'
		else:
			suff=''
		df_out['Variable']=var+suff
			

		return df_out

		

	def pvalue_slopes(self,df,var,depvar,splitvar,splitval,val_comp=1,return_all=False):
	
		mask_aspnnull=(pd.notnull(df[var]))
		mask_split=(df[splitvar]>splitval)

		trans = StandardScaler()
		df[var+'_std']=trans.fit_transform(np.asarray(df[var]).reshape(-1, 1))
		
		slope_ap, intercept_ap, r_value_ap, p_value_ap, std_err_ap = \
		stats.linregress(df[mask_aspnnull][var+'_std'],df[mask_aspnnull][depvar])
		
		
		slope1, intercept1, r_value1, p_value1, std_err1 = \
		stats.linregress(df[mask_aspnnull&mask_split][var+'_std'],df[mask_aspnnull&mask_split][depvar])


		slope2, intercept2, r_value2, p_value2, std_err2 = \
		stats.linregress(df[mask_aspnnull&~mask_split][var+'_std'],df[mask_aspnnull&~mask_split][depvar])

		
		x=df[mask_aspnnull&mask_split][var+'_std']
		tinv = lambda p, df: abs(t.ppf(p/2, df))
		ts = tinv(0.05, len(x)-2)
		CI1=ts*std_err1

		x=df[mask_aspnnull&~mask_split][var+'_std']
		tinv = lambda p, df: abs(t.ppf(p/2, df))
		ts = tinv(0.05, len(x)-2)
		CI1=ts*std_err2


		numerator = slope1 - slope2
		denominator = pow((pow(std_err1,2) + pow(std_err2,2)), 1/2)
		z=numerator/denominator  
		print(z)

		p_value = stats.norm.sf(abs(z))
		print(p_value)
		
		#val_comp is 0 if we are comparing the top value as numerator from the split vars else it's 1
		if val_comp==0:
			slope_diff=(slope2/slope1) 
		else:
			slope_diff=(slope1/slope2) 

		
		print('Slope Difference: '+str(slope_diff))

		if return_all:
			return slope_diff,slope1,slope2,p_value
		else:
			return slope_diff,p_value

	def varsplit(self,df,splitvar,splitval,cols,depvar):
		print("yah!")
		mask=(df[splitvar]>splitval)
		allvals=[]
		split1vals=[]
		split2vals=[]
		for col in [c for c in cols if c!=depvar]: 
			#if 'age_when' not in col:
				#df=self.agenorm2(df,col)
			allval=self.slope(df=df,var=col,depvar=depvar)
			splitval1=self.slope(df=df[mask],var=col,depvar=depvar)
			print(df[mask].shape)
			print(df[mask]['PD'].sum())
			splitval2=self.slope(df=df[~mask],var=col,depvar=depvar)
			allvals.append(allval)
			split1vals.append(splitval1)
			split2vals.append(splitval2)

		sum_df=pd.DataFrame({'column_name':[c for c in cols if c!=depvar],'allvals':allvals,
			'split1vals':split1vals,'split2vals':split2vals})
		for var in ['allvals','split1vals','split2vals']:
			sum_df[var+'_slope']=sum_df[var].apply(lambda x:x[0])
			sum_df[var+'_slope_pval']=sum_df[var].apply(lambda x:x[3])
		sum_df.drop(columns=['allvals','split1vals','split2vals'],inplace=True)

		return sum_df

	def death_exclusions(self,df,disease):

		
		death=pd.read_parquet(self.path+'deaths_test.parquet')
		death=death[(death['date_of_death_f40000_0_0']!='nan')]
		death['date_of_death_f40000_0_0']=pd.to_datetime(death['date_of_death_f40000_0_0'])

		nondis_deaths=list(death['eid'][~(death['eid'].isin(df['eid'][(df[disease]==1)]))])

		return nondis_deaths


	def ttest(self,df,bdown,var,disease='PD'):
		ttest_vals=stats.ttest_ind(df[(df['dis_stage']==bdown)][var], 
				   df[(df['dis_stage']=='No '+disease)][var])
		
		return ttest_vals

	def get_dis_stage(self,x,disease='PD'):
		if x<-10:
			y='<10'
		elif x>=-10 and x<=-5:
			y='-10>-5'
		elif x>-5 and x<=0:
			y='-5>0'
		elif x>0 and x<=5:
			y='0>5'
		elif x>5:
			y='5+'
		else:
			y='No '+disease

		return y

	def getpval_arr(self,pval_array,length=3):

		pvals_out=[]
		for k in list(np.arange(length)):
			sig='ns'

			if pval_array[k]<0.001:
				sig='***'
			elif pval_array[k]<0.01:
				sig='**'
			elif pval_array[k]<0.05:
				sig='*'
			pvals_out.append(sig)

		return pvals_out






	def analysis_boxplots(self,df,dis_date='parkins_date',disease='PD',vars=['igf1_f30770_0_0'],
	splitvar='sex_f31_0_0',agemin=50,agemax=70,labels=dict({1:'Female',0:'Male'}),varnames='test',exc_deaths=False,dis_label=True,
	agenormvars=[],agevar='age_when_attended_assessment_centre_f21003_0_0',min_dis_bef=-20,max_dis_aft=15):

		df=df.copy()



		compgroups=list(['No '+disease,'-10>-5','-5>0','0>5'])

		cols_use=['eid','years_'+disease,disease,splitvar,agevar]+vars

		mask=((df['years_'+disease]<=max_dis_aft)&(df['years_'+disease]>=min_dis_bef))|pd.isnull(df['years_'+disease])
		df=df.loc[mask,cols_use]

		
		df['dis_stage']=df.apply(lambda x:self.get_dis_stage(disease=disease,x=x['years_'+disease]),axis=1)

		#df['years_'+disease].apply(self.get_dis_stage(disease=disease))

		
		compgroups=[c for c in compgroups if c in list(df['dis_stage'].unique())]

		#print(compgroups)

		#for v in vars:
			#print(v)
			#print(df[v].sample(10))

		for a in agenormvars:
			df=self.agenorm(df,a)

		k=len(vars)
		fig = plt.figure(figsize=(15*k, 10*k))
		grid = plt.GridSpec(k, k, hspace=0.45, wspace=0.3)

		ttestvals=[]
		lq_vals=[]
		med_vals=[]
		uq_vals=[]
		pvallist=[]
		varnameslist=[]
		splitnames=[]
		comp_groups=[]
		std_vals=[]
		grpsize_arr=[]


		splitvars=list(set(list(df.loc[pd.notnull(df[splitvar]),splitvar].unique())))


		for i,v in enumerate(vars):
			

			for j,t in enumerate(splitvars):

				#print(i)
				#print(labels[i])
				#mask1=pd.isnull(df[dis_date])
				
				#max_mask=(df[v]<df[v].quantile(0.99))


				mask=(pd.notnull(df[v]))&(df[v]!=np.inf)&(df[v]!=np.nan)&(df[splitvar]==t)

				
				

				df_use=df.loc[mask,]

				ax=fig.add_subplot(grid[i, j])
				avg=df_use[v].mean()

				#print(v,df_use[v].max())
				

				df_use.sort_values(by='dis_stage',inplace=True)
				

				ax=sns.boxplot(x=df_use['dis_stage'],y=df_use[v],order=compgroups,showfliers = False,color='skyblue')
				plt.xticks(fontsize='35')
				plt.yticks(fontsize='35')
				#plt.ylabel(v, fontsize=24)
				if v in self.yaxis_units:
					unit=self.yaxis_units[v]
				else:
					unit='%'
				plt.ylabel(unit,fontsize='30')
				plt.xlabel(labels[t]+'s: '+str(ml.mapvar(v)), fontsize='35')
				plt.xlabel('Years of '+disease)
				plt.title(labels[t]+'s: '+str(ml.mapvar(v)), fontsize='35')

				#whisker locations - find top within group whisker
				max_val=df_use[v].max()
				min_val=df_use[v].min()
				q_25=df_use[v].quantile(0.25)
				q_75=df_use[v].quantile(0.75)
				iqr=q_75-q_25
			   
				iqr_pos = q_75+1.5*iqr if (q_75+1.5*iqr)<max_val else max_val
				iqr_neg = q_25-1.5*iqr if (q_25-1.5*iqr)>min_val else min_val

				iqr_pos_arr=[]
				iqr_neg_arr=[]
				pvallist_small=[]
				#mask_use=pd.notnull(df[v])

				for q,m in enumerate(compgroups):

					ttest_vals=self.ttest(df_use,m,v,disease=disease)


					mask_dis_stage=(df_use['dis_stage']==m)

					df_use_ds=df_use.loc[mask_dis_stage,]

					max_val=df_use_ds[v].max()
					min_val=df_use_ds[v].min()
					q_25=df_use_ds[v].quantile(0.25)
					q_75=df_use_ds[v].quantile(0.75)
					med=df_use_ds[v].quantile(0.5)
					grpsize=df_use_ds.shape[0]

					

					iqr=q_75-q_25

					std_val=round(df_use_ds[v].std(),3)

					iqr_pos = q_75+1.5*iqr if (q_75+1.5*iqr)<max_val else max_val
					iqr_pos_arr.append(iqr_pos)
					iqr_neg = q_25-1.5*iqr if (q_25-1.5*iqr)>min_val else min_val
					iqr_neg_arr.append(iqr_neg)

				   
					ttest_val_inc=round(df_use_ds[v].mean(),3)#round(ttest_vals[0],3)
					pval_inc=round(ttest_vals[1],6)

					grpsize_arr.append(grpsize)
					ttestvals.append(ttest_val_inc)
					med_vals.append(med)
					lq_vals.append(q_25)
					uq_vals.append(q_75)


					pvallist.append(pval_inc)
					pvallist_small.append(pval_inc)
					varnameslist.append(v)
					splitnames.append(t)
					comp_groups.append(m)
					std_vals.append(std_val)

				#print(pvallist_small)
				pvals_signs=self.getpval_arr(pval_array=pvallist_small,length=len(compgroups))

				#for k in list(np.arange(len(compgroups))+1):

				
				for k in [1,2,3]:

				
					sig=pvals_signs[k]

					if sig !='ns':
						x1, x2 = 0, k  
						y, h, col = iqr_pos + (iqr_pos_arr[k]-iqr_neg_arr[k])/5, k*(iqr_pos_arr[k]-iqr_neg_arr[k])/5, 'black'
						plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c=col)
						#plt.text((x1+x2)*.5, y+h, 'p= '+str(pvallist_small[k])+' '+str(sig), ha='center', va='bottom', color=col,
						#	fontsize='24')
						plt.text((x1+x2)*.5, y+h*0.95, str(sig), ha='center', va='bottom', color=col,
							fontsize='24')




		plt.savefig(self.path_figures_pd+self.date_run+"_"+varnames+'.jpg', dpi=300,bbox_inches='tight')
		plt.show()
		
		pvals_df=pd.DataFrame({'Variable':varnameslist,'Split':splitnames,'Group Size':grpsize_arr,'Years into disease':comp_groups,
			'Mean':ttestvals,'Median':med_vals,'lower quartile':lq_vals,
			'upper quartile':uq_vals,'p value':pvallist,'standard deviations':std_vals})
		outs=dict({'df':df,'pvals_df':pvals_df})

		return outs

	def replot_figs_adj(self,df,vars,pval_dict,splitvar='sex_f31_0_0',disease='PD',varnames='test'):

		compgroups=df['dis_stage'].unique()
		#gends=df[splitvar].unique()

		splitvars=list(set(list(df.loc[pd.notnull(df[splitvar]),splitvar].unique())))

		labels=dict({1:'Female',0:'Male',1.0:'Female',0.0:'Male'})

		k=len(vars)
		fig = plt.figure(figsize=(15*k, 10*k))
		grid = plt.GridSpec(k, k, hspace=0.45, wspace=0.3)	

		for i,v in enumerate(vars):
			for j,t in enumerate(splitvars):

				mask=(pd.notnull(df[v]))&(df[v]!=np.inf)&(df[v]!=np.nan)&(df[splitvar]==t)
				df1=df.loc[mask,]

				ax=fig.add_subplot(grid[i, j])
				ax=sns.boxplot(x=df1['dis_stage'],y=df1[v],order=compgroups,showfliers = False, color='skyblue')

				plt.xticks(fontsize='35')
				plt.yticks(fontsize='35')
				#plt.ylabel(v, fontsize=24)
				if v in self.yaxis_units:
					unit=self.yaxis_units[v]
				else:
					unit='%'
				plt.ylabel(unit,fontsize='30')
				plt.xlabel(labels[t]+'s: '+str(ml.mapvar(v)), fontsize='35')
				plt.xlabel('Years of '+disease)
				plt.title(labels[t]+'s: '+str(ml.mapvar(v)), fontsize='35')

				pval_list=[]
				iqr_pos_arr=[]
				iqr_neg_arr=[]

				for q,m in enumerate(compgroups):

					bdown=str(v)+str(t)+"'"+str(m)

					mask=(df1['dis_stage']==m)
					df2=df1.loc[mask,]
					
					

					max_val=df2[v].max()
					min_val=df2[v].min()
					q_25=df2[v].quantile(0.25)
					q_75=df2[v].quantile(0.75)
					med=df2[v].quantile(0.5)

					iqr=q_75-q_25
					iqr_pos = q_75+1.5*iqr if (q_75+1.5*iqr)<max_val else max_val
					iqr_pos_arr.append(iqr_pos)
					iqr_neg = q_25-1.5*iqr if (q_25-1.5*iqr)>min_val else min_val
					iqr_neg_arr.append(iqr_neg)

					#print(pval_dict)
					p_val=pval_dict[bdown]
					pval_list.append(p_val)
					
				pvals_signs=self.getpval_arr(pval_array=pval_list,length=len(compgroups))

				for k in [1,2,3]:
					sig=pvals_signs[k]
					if sig !='ns':
						x1, x2 = 0, k  
						y, h, col = iqr_pos + (iqr_pos_arr[k]-iqr_neg_arr[k])/5, k*(iqr_pos_arr[k]-iqr_neg_arr[k])/5, 'black'
						plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c=col)
						#plt.text((x1+x2)*.5, y+h, 'p= '+str(pvallist_small[k])+' '+str(sig), ha='center', va='bottom', color=col,
						#	fontsize='24')
						plt.text((x1+x2)*.5, y+h*0.95, str(sig), ha='center', va='bottom', color=col,
							fontsize='24')

					#calc positioning here

				
			plt.savefig(self.path_figures_pd+self.date_run+"_"+varnames+'.jpg', dpi=300,bbox_inches='tight')

		return None

		# work out locations in the chart and what to put where

		# work out the adjusted p values and info from dataframe




	def disease_traj(self,df=None,labelfile='labels_dates_test.parquet',dis_date='parkins_date',disease='PD',vars=['igf1_f30770_0_0'],
	splitvar='sex_f31_0_0',agemin=50,agemax=70,labels=['Female','Male'],varnames='IGF1',plots='lineplots',ttest_use=False,
	agegendnormvars=[],exc_deaths=False,dis_label=True):

		"""
		Brings in the full data and disease date so we can model variables averages across trajectory of patient journey
		
		"""

		ml=IDEARs_funcs()

		if dis_label:
			colsimport=list(set(list(['eid','age_when_attended_assessment_centre_f21003_0_0',splitvar,disease]+vars)))
		else:
			colsimport=list(set(list(['eid','age_when_attended_assessment_centre_f21003_0_0',splitvar]+vars)))

		if df is None:
			df_model=pd.read_parquet(self.path+'df_all_final.parquet',columns=colsimport)
		else:
			df_model=df.copy()

		if dis_label:
			labelcols=['eid',dis_date]
		else:
			labelcols=['eid',dis_date,disease]
		df_dates=pd.read_parquet(self.path+labelfile)[labelcols]
		df_model_orig=pd.read_parquet(self.path+'df_model_test.parquet')[['eid','date_of_attending_assessment_centre_f53_0_0']]

		df_dates['eid']=df_dates['eid'].astype(str)
		df_model['eid']=df_model['eid'].astype(str)
		df_model_orig['eid']=df_model_orig['eid'].astype(str)
		df_test=pd.merge(df_model,df_dates,on='eid',how='left')
		df_test=pd.merge(df_test,df_model_orig,on='eid',how='left')
		mask3=(df_test['age_when_attended_assessment_centre_f21003_0_0']>=agemin)&\
	 (df_test['age_when_attended_assessment_centre_f21003_0_0']<=agemax)

		df_test[disease].fillna(0,inplace=True)
		
		mask_keep=(df_test[splitvar]==0)|(df_test[splitvar]==1)&mask3
		df_test=df_test[mask_keep]

		if exc_deaths:
			excs=self.death_exclusions(df_test,disease)
			mask=(~df_test['eid'].isin(excs))
			df_test=df_test[mask]


		df_test['disease']=0
		mask=pd.notnull(df_test[dis_date])
		df_test['disease'][mask]=1

		

		df_test['date_of_attending_assessment_centre_f53_0_0']=\
	pd.to_datetime(df_test['date_of_attending_assessment_centre_f53_0_0'])
		df_test['years_'+disease]=-round((df_test[dis_date]-df_test['date_of_attending_assessment_centre_f53_0_0']).dt.days/365)
		



		k=len(vars)

		fig = plt.figure(figsize=(15*k, 10*k))
		grid = plt.GridSpec(k, k, hspace=0.45, wspace=0.3)

		ttestvals=[]
		lq_vals=[]
		med_vals=[]
		uq_vals=[]
		pvallist=[]
		varnameslist=[]
		splitnames=[]
		comp_groups=[]
		std_vals=[]

		if len(agegendnormvars)>0:
			df_test=self.age_gend_norm_mult(df_test,vars)

		
		for j,v in enumerate(vars):

			for i,t in enumerate(df_test[splitvar][pd.notnull(df_test[splitvar])].unique()):

				#print(i)
				#print(labels[i])
				mask=pd.isnull(df_test[dis_date])
				mask_split=(df_test[splitvar]==i)
				mask2=((df_test['years_'+disease]>-10)&(df_test['years_'+disease]<5))|pd.isnull(df_test['years_'+disease])
				mask3=(df_test['age_when_attended_assessment_centre_f21003_0_0']>=agemin)&\
				(df_test['age_when_attended_assessment_centre_f21003_0_0']<=agemax)

			   
				ax=fig.add_subplot(grid[j, i])
				avg=df_test[mask&mask3&mask_split][v].mean()

				mask_12=(df_test['years_'+disease]<-5)&(df_test['years_'+disease]>-10)
				mask_5=(df_test['years_'+disease]<-0)&(df_test['years_'+disease]>=-5)
				mask_05=(df_test['years_'+disease]<5)&(df_test['years_'+disease]>=0)
				mask_no_pd=(pd.isnull(df_test['years_'+disease]))&(df_test[disease]==0)


				mask_v=(df_test[v]<df_test[v].quantile(0.95))&(df_test[v]>=df_test[v].quantile(0.05))
				df_test['dis_stage']=np.nan
				df_test['dis_stage'][mask_12]='-10>-5'#"2: 5-10 years pre diag"
				df_test['dis_stage'][mask_5]='-5>0'#"3: 0-5 years pre diag"
				df_test['dis_stage'][mask_05]='0>5'#"4: 0-5 years post diag"
				df_test['dis_stage'][mask_no_pd]='No '+disease#"1: No PD"

				if plots=='lineplots':

					

					ax=sns.lineplot(data=df_test[mask2&mask3&mask_split], 
					x='years_'+disease, y=v,estimator='mean',
					palette = 'Greys_r',linewidth = 4)
					ax.axhline(avg,color='red')

					range_vals=df_test[mask2&mask3&mask_split][v].quantile(0.95)-\
				df_test[mask2&mask3&mask_split][v].quantile(0.05)


					plt.text(0,max(0,avg+range_vals/100),labels[i]+' levels for non '+disease,fontsize=24)
					plt.title=str(v) + str(labels[i])

					plt.xticks(fontsize='24')
					plt.yticks(fontsize='24')
					plt.xlabel('years_'+disease+'_'+str(labels[i]), fontsize=24)
					plt.ylabel(v, fontsize=24)
					#plt.savefig('figures/'+'fig4'+"_"+v+' '+str(labels[i])+'.svg', dpi=300)
					#plt.show()

				elif plots=='boxplots':


					mask_use=mask2&mask3&mask_split
					df_test.sort_values(by='dis_stage',inplace=True)
					ax=sns.boxplot(x=df_test['dis_stage'][mask_use],y=df_test[v][mask_use],
						order=['No '+disease,'-10>-5','-5>0','0>5'],showfliers = False,color='skyblue')
					plt.xticks(fontsize='35')
					plt.yticks(fontsize='35')
					#plt.ylabel(v, fontsize=24)
					plt.ylabel(self.yaxis_units[v],fontsize='30')
					plt.xlabel(labels[i]+'s: '+str(ml.mapvar(v)), fontsize='35')
					plt.xlabel('Years of '+disease)
					plt.title(labels[i]+'s: '+str(ml.mapvar(v)), fontsize='35')

					#whisker locations - find top within group whisker
					max_val=df_test[v][mask_use].max()
					min_val=df_test[v][mask_use].min()
					q_25=df_test[v][mask_use].quantile(0.25)
					q_75=df_test[v][mask_use].quantile(0.75)
					iqr=q_75-q_25
				   
					iqr_pos = q_75+1.5*iqr if (q_75+1.5*iqr)<max_val else max_val
					iqr_neg = q_25-1.5*iqr if (q_25-1.5*iqr)>min_val else min_val
					


					# statistical annotation
					#x1, x2 = 0, 3   # columns 'Sat' and 'Sun' (first column: 0, see plt.xticks())
					#y, h, col = iqr_pos + (iqr_pos-iqr_neg)/5, (iqr_pos-iqr_neg)/20, 'k'
					#plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c=col)
					#plt.text((x1+x2)*.5, y+h, "ns", ha='center', va='bottom', color=col)


					#if df_test[mask_use][v].nunique()>5:
					   # plt.ylim(df_test[mask_use][v].quantile(0),df_test[mask_use][v].quantile(0.99))
					#plt.savefig('figures/'+'fig4'+"_"+v+' '+str(labels[i])+'.svg', dpi=300)
					

					

				if ttest_use:

					#print(df_test['dis_stage'].value_counts())

					mask_v=pd.notnull(df_test[v])

					mask_use=mask2&mask3&mask_split&mask_v

					#compgroups=list(['1: No PD','2: 5-10 years pre diag','3: 0-5 years pre diag','4: 0-5 years post diag'])
					compgroups=list(['No PD','-10>-5','-5>0','0>5'])
				   
					iqr_pos_arr=[]
					iqr_neg_arr=[]
					pvallist_small=[]
					for q,m in enumerate(compgroups):

						ttest_vals=self.ttest(df_test[mask_use],m,v,disease=disease)


						mask_dis_stage=(df_test['dis_stage']==m)

						max_val=df_test[v][mask_use&mask_dis_stage].max()
						min_val=df_test[v][mask_use&mask_dis_stage].min()
						q_25=df_test[v][mask_use&mask_dis_stage].quantile(0.25)
						q_75=df_test[v][mask_use&mask_dis_stage].quantile(0.75)
						med=df_test[v][mask_use&mask_dis_stage].quantile(0.5)

						

						iqr=q_75-q_25

						std_val=round(df_test[v][mask_use&mask_dis_stage].std(),3)

						iqr_pos = q_75+1.5*iqr if (q_75+1.5*iqr)<max_val else max_val
						iqr_pos_arr.append(iqr_pos)
						iqr_neg = q_25-1.5*iqr if (q_25-1.5*iqr)>min_val else min_val
						iqr_neg_arr.append(iqr_neg)

					   
						ttest_val_inc=round(df_test[mask_use&mask_dis_stage][v].mean(),3)#round(ttest_vals[0],3)
						pval_inc=round(ttest_vals[1],6)
						ttestvals.append(ttest_val_inc)
						med_vals.append(med)
						lq_vals.append(q_25)
						uq_vals.append(q_75)


						pvallist.append(pval_inc)
						pvallist_small.append(pval_inc)
						varnameslist.append(v)
						splitnames.append(i)
						comp_groups.append(m)
						std_vals.append(std_val)

					# statistical annotation



					for k in [1,2,3]:
						sig=''

						if pvallist_small[k]<0.001:
							sig='***'
						elif pvallist_small[k]<0.005:
							sig='**'
						elif pvallist_small[k]<0.05:
							sig='*'

						if sig !='':
							x1, x2 = 0, k  
							y, h, col = iqr_pos + (iqr_pos_arr[k]-iqr_neg_arr[k])/5, k*(iqr_pos_arr[k]-iqr_neg_arr[k])/5, 'black'
							plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c=col)
							#plt.text((x1+x2)*.5, y+h, 'p= '+str(pvallist_small[k])+' '+str(sig), ha='center', va='bottom', color=col,
							#	fontsize='24')
							plt.text((x1+x2)*.5, y+h*0.95, str(sig), ha='center', va='bottom', color=col,
								fontsize='24')


					

		
		plt.savefig(self.pathfig+'fig_'+self.date_run+"_"+varnames+'.jpg', dpi=300,bbox_inches='tight')
		plt.show()
		if ttest_use:
			pvals_df=pd.DataFrame({'var':varnameslist,'split':splitnames,'compgroup':comp_groups,
				'mean_val':ttestvals,'median':med_vals,'lower_quartile':lq_vals,'upper_quartile':uq_vals,'pvals':pvallist,'std_vals':std_vals})
			df_test=[df_test,pvals_df]



		return df_test



