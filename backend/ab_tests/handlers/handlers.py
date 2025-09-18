import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn as sk
import scipy.stats as stats
import statsmodels as smd
import logging
import os
from rest_framework.response import Response
from django.http.response import HttpResponseBadRequest
from math import sqrt


def count_mde(
    filepath_or_buffer,
    test_column,
    control_column,
    alpha = 0.05,
    beta = 0.2
):
    try:
        df = pd.read_csv(filepath_or_buffer=filepath_or_buffer)
        test = df[test_column]
        control = df[control_column]
        if test.empty or control.empty:
            raise ValueError("Error while extracting columns from the dataset")
        z = stats.norm(loc=0, scale=1)
        n1 = len(test)
        n2 = len(control)
        mde = (z.ppf(1- alpha/2) + z.ppf(1- beta))*sqrt(test.var(ddof=1)/n1 + control.var(ddof=1)/n2)
        result = {
            "MDE":mde,
            "MDE_%":100*(mde / np.mean(pd.concat((test, control), axis=0, copy=True))),
            "test_size":n1,
            "control_size":n2,
        }
        return Response(result), result
    except Exception as e:
        logging.error("Error while calculating")
        logging.exception(e)
        return HttpResponseBadRequest("Error while calculating", e.__str__()), None


def count_n(
    filepath_or_buffer,
    test_column,
    control_column,
    alpha,
    beta,
    mde,
    k=1
):
    try:
        df = pd.read_csv(filepath_or_buffer=filepath_or_buffer)
        test = df[test_column]
        control = df[control_column]
        if test.empty or control.empty:
            raise ValueError("Error while extracting columns from the dataset")
        z = stats.norm(loc=0, scale=1)
        n1 = len(test)
        n2 = len(control)
        n = (test.var(ddof=1) + control.var(ddof=1))/((mde/(z.ppf(1- alpha/2) + z.ppf(1- beta)))**2)
        

        
        result = {
            "MDE":mde,
            "MDE_%":100*(mde / np.mean(pd.concat((test, control), axis=0, copy=True))),
            "n":n,
            "n_total":2*n,
            "test_size":n,
            "control_size":n,
        }
        return Response(result), result
    except Exception as e:
        logging.error("Error while calculating")
        logging.exception(e)
        return HttpResponseBadRequest("Error while calculating", e.__str__()), None


def z_test(
    filepath_or_buffer,
    test_column,
    control_column,
    alpha,
    beta,
):
    try:
        df = pd.read_csv(filepath_or_buffer=filepath_or_buffer)
        test = df[test_column]
        control = df[control_column]
        if test.empty or control.empty:
            raise ValueError("Error while extracting columns from the dataset")
        z = stats.norm(loc=0, scale=1)
        n1 = len(test)
        n2 = len(control)
        mean1, mean2 = test.mean(), control.mean()
        var1, var2 = test.var(ddof=0), control.var(ddof=0)

        z = (mean1 - mean2) / np.sqrt(var1/n1 + var2/n2)
        p = 2 * (1 - stats.norm.cdf(abs(z)))
        pearson_obj = stats.pearsonr(test, control)
        spearman_obj = stats.spearmanr(test, control)

        pearson = pearson_obj[0]
        spearman = spearman_obj[0]

        pearson_p = pearson_obj[1]
        spearman_p = spearman_obj[1]

        warning = "Z-test should be used when you know population variance, not sample variance.\n"
        if pearson > 0.5:
            warning += f"Test and control may be dependent (Pearson={pearson:.2f})\n"
        if spearman > 0.5:
            warning += f"Test and control may be dependent (Spearman={spearman:.2f})\n"
        if pearson > 0.5 and spearman > 0.5:
            warning += "Test and control appear independent\n"

        result = {
            "n1": n1,
            "n2": n2,
            "z": z,
            "p": p,
            "var_test":var1,
            "var_control":var2,
            "mean_test":mean1,
            "mean_control":mean2,
            "effect": 1 if p<alpha else 0,
            "pearson":pearson,
            "spearman":spearman,
            "pearson_p":pearson_p,
            "spearman_p":spearman_p,
            "warning":warning
        }

        return Response(result), result
    except Exception as e:
        logging.error("Error while calculating")
        logging.exception(e)
        return HttpResponseBadRequest("Error while calculating", e.__str__()), None


def t_test(
    filepath_or_buffer,
    test_column,
    control_column,
    alpha,
    beta,
    related = False
):
    try:
        df = pd.read_csv(filepath_or_buffer=filepath_or_buffer)
        test = df[test_column]
        control = df[control_column]
        if test.empty or control.empty:
            raise ValueError("Error while extracting columns from the dataset")

        n1 = len(test)
        n2 = len(control)
        mean1, mean2 = test.mean(), control.mean()
        var1, var2 = test.var(ddof=1), control.var(ddof=1)
        if related:
            t_stat, p_value = stats.ttest_rel(test, control)
        else:
            t_stat, p_value = stats.ttest_ind(test, control)
        pearson_obj = stats.pearsonr(test, control)
        spearman_obj = stats.spearmanr(test, control)

        pearson = pearson_obj[0]
        spearman = spearman_obj[0]

        pearson_p = pearson_obj[1]
        spearman_p = spearman_obj[1]

        warning = "T-test should be used when the data is Normal, or the N > 30. Also, the variations should be equal. Else, try usig Welch`s test\n"
        if pearson_p < alpha:
            warning += f"Test and control may be dependent (Pearson={pearson:.2f})\n"
        if spearman_p < alpha:
            warning += f"Test and control may be dependent (Spearman={spearman:.2f})\n"
        if pearson_p >= alpha and spearman_p >= alpha:
            warning += "Test and control appear independent\n"

        result = {
            "n1": n1,
            "n2": n2,
            "t": t_stat,
            "p": p_value,
            "var_test":var1,
            "var_control":var2,
            "mean_test":mean1,
            "mean_control":mean2,
            "effect": 1 if p_value<alpha else 0,
            "pearson":pearson,
            "spearman":spearman,
            "pearson_p":pearson_p,
            "spearman_p":spearman_p,
            "warning":warning
        }

        return Response(result), result
    except Exception as e:
        logging.error("Error while calculating")
        logging.exception(e)
        return HttpResponseBadRequest("Error while calculating", e.__str__()), None



def chi_2test(
    filepath_or_buffer,
    test_column,
    control_column,
    alpha,
    beta,
    related = False
):
    try:
        df = pd.read_csv(filepath_or_buffer=filepath_or_buffer)
        test = df[test_column]
        control = df[control_column]
        if test.empty or control.empty:
            raise ValueError("Error while extracting columns from the dataset")

        mode_test = test.mode()
        mode_controle = control.mode()

        n1 = len(test)
        n2 = len(control)

        table = pd.crosstab(df[test_column], df[control_column])
        chi2_stat, p_value, dof, expected = stats.chi2_contingency(table)


        warning = "Сhi-square should be used when the data is categorial only\n"

        result = {
            "n1": n1,
            "n2": n2,
            "p": p_value,
            "chi2_stat":chi2_stat,
            "p_value":p_value,
            "dof":dof,
            "expected":expected,
            "mode_test":mode_test,
            "mode_control":mode_controle,
            "effect": 1 if p_value<alpha else 0,
            "warning":warning
        }

        return Response(result), result
    except Exception as e:
        logging.error("Error while calculating")
        logging.exception(e)
        return HttpResponseBadRequest("Error while calculating", e.__str__()), None


def ks_2test(
    filepath_or_buffer,
    test_column,
    control_column,
    alpha,
    beta,
    related = False
):
    try:
        df = pd.read_csv(filepath_or_buffer=filepath_or_buffer)
        test = df[test_column]
        control = df[control_column]
        if test.empty or control.empty:
            raise ValueError("Error while extracting columns from the dataset")

        n1 = len(test)
        n2 = len(control)
        mean1, mean2 = test.mean(), control.mean()
        var1, var2 = test.var(ddof=1), control.var(ddof=1)
        
        pearson_obj = stats.pearsonr(test, control)
        spearman_obj = stats.spearmanr(test, control)

        pearson = pearson_obj[0]
        spearman = spearman_obj[0]

        pearson_p = pearson_obj[1]
        spearman_p = spearman_obj[1]

        stat, p_value = stats.ks_2samp(test, control)

        warning = "KS-test might be too optimistic\n"
        if pearson_p < alpha:
            warning += f"Test and control may be dependent (Pearson={pearson:.2f})\n"
        if spearman_p < alpha:
            warning += f"Test and control may be dependent (Spearman={spearman:.2f})\n"
        if pearson_p >= alpha and spearman_p >= alpha:
            warning += "Test and control appear independent\n"

        result = {
            "n1": n1,
            "n2": n2,
            "stat": stat,
            "p": p_value,
            "var_test":var1,
            "var_control":var2,
            "mean_test":mean1,
            "mean_control":mean2,
            "effect": 1 if p_value<alpha else 0,
            "pearson":pearson,
            "spearman":spearman,
            "pearson_p":pearson_p,
            "spearman_p":spearman_p,
            "warning":warning
        }

        return Response(result), result
    except Exception as e:
        logging.error("Error while calculating")
        logging.exception(e)
        return HttpResponseBadRequest("Error while calculating", e.__str__()), None


def cramer_test(
    filepath_or_buffer,
    test_column,
    control_column,
    alpha,
    beta,
    related = False
):
    try:
        df = pd.read_csv(filepath_or_buffer=filepath_or_buffer)
        test = df[test_column]
        control = df[control_column]
        if test.empty or control.empty:
            raise ValueError("Error while extracting columns from the dataset")

        n1 = len(test)
        n2 = len(control)
        mean1, mean2 = test.mean(), control.mean()
        var1, var2 = test.var(ddof=1), control.var(ddof=1)
        
        pearson_obj = stats.pearsonr(test, control)
        spearman_obj = stats.spearmanr(test, control)

        pearson = pearson_obj[0]
        spearman = spearman_obj[0]

        pearson_p = pearson_obj[1]
        spearman_p = spearman_obj[1]

        result = stats.cramervonmises_2samp(test, control)
        stat, p_value = result.statistic, result.pvalue
        warning = "Kramer`s test requires the distributions to be continuous\n"
        if pearson_p < alpha:
            warning += f"Test and control may be dependent (Pearson={pearson:.2f})\n"
        if spearman_p < alpha:
            warning += f"Test and control may be dependent (Spearman={spearman:.2f})\n"
        if pearson_p >= alpha and spearman_p >= alpha:
            warning += "Test and control appear independent\n"

        result = {
            "n1": n1,
            "n2": n2,
            "stat": stat,
            "p": p_value,
            "var_test":var1,
            "var_control":var2,
            "mean_test":mean1,
            "mean_control":mean2,
            "effect": 1 if p_value<alpha else 0,
            "pearson":pearson,
            "spearman":spearman,
            "pearson_p":pearson_p,
            "spearman_p":spearman_p,
            "warning":warning
        }

        return Response(result), result
    except Exception as e:
        logging.error("Error while calculating")
        logging.exception(e)
        return HttpResponseBadRequest("Error while calculating", e.__str__()), None


def u_test(
    filepath_or_buffer,
    test_column,
    control_column,
    alpha,
    beta,
    related = False
):
    try:
        df = pd.read_csv(filepath_or_buffer=filepath_or_buffer)
        test = df[test_column]
        control = df[control_column]
        if test.empty or control.empty:
            raise ValueError("Error while extracting columns from the dataset")

        n1 = len(test)
        n2 = len(control)
        mean1, mean2 = test.mean(), control.mean()
        var1, var2 = test.var(ddof=1), control.var(ddof=1)
        
        pearson_obj = stats.pearsonr(test, control)
        spearman_obj = stats.spearmanr(test, control)

        pearson = pearson_obj[0]
        spearman = spearman_obj[0]

        pearson_p = pearson_obj[1]
        spearman_p = spearman_obj[1]

        result = stats.mannwhitneyu(test, control)
        stat, p_value = result.statistic, result.pvalue
        warning = "Kramer`s test requires the distributions to be continuous\n"
        if pearson_p < alpha:
            warning += f"Test and control may be dependent (Pearson={pearson:.2f})\n"
        if spearman_p < alpha:
            warning += f"Test and control may be dependent (Spearman={spearman:.2f})\n"
        if pearson_p >= alpha and spearman_p >= alpha:
            warning += "Test and control appear independent\n"

        result = {
            "n1": n1,
            "n2": n2,
            "stat": stat,
            "p": p_value,
            "var_test":var1,
            "var_control":var2,
            "mean_test":mean1,
            "mean_control":mean2,
            "effect": 1 if p_value<alpha else 0,
            "pearson":pearson,
            "spearman":spearman,
            "pearson_p":pearson_p,
            "spearman_p":spearman_p,
            "warning":warning
        }

        return Response(result), result
    except Exception as e:
        logging.error("Error while calculating")
        logging.exception(e)
        return HttpResponseBadRequest("Error while calculating", e.__str__()), None


def lilleforce_test(
    filepath_or_buffer,
    test_column,
    control_column,
    alpha,
    beta,
    related = False
):
    try:
        df = pd.read_csv(filepath_or_buffer=filepath_or_buffer)
        test = df[test_column]
        control = df[control_column]
        if test.empty or control.empty:
            raise ValueError("Error while extracting columns from the dataset")

        n1 = len(test)
        n2 = len(control)
        mean1, mean2 = test.mean(), control.mean()
        var1, var2 = test.var(ddof=1), control.var(ddof=1)
        
        pearson_obj = stats.pearsonr(test, control)
        spearman_obj = stats.spearmanr(test, control)

        pearson = pearson_obj[0]
        spearman = spearman_obj[0]

        pearson_p = pearson_obj[1]
        spearman_p = spearman_obj[1]

        from statsmodels.stats.diagnostic import lilliefors
        result = lilliefors(test, dist='norm')
        result_control = lilliefors(control, dist='norm')
        stat, p_value = result[0], result[1]
        control_stat = result_control[0]
        control_p = result_control[1]
        warning = "Lilliefors test can be sensitive to the outliers, try using Shapiro-Wilke test too\n"
        if pearson_p < alpha:
            warning += f"Test and control may be dependent (Pearson={pearson:.2f})\n"
        if spearman_p < alpha:
            warning += f"Test and control may be dependent (Spearman={spearman:.2f})\n"
        if pearson_p >= alpha and spearman_p >= alpha:
            warning += "Test and control appear independent\n"
        if control_p < alpha:
            warning += f"Control group is NOT from normal distribution (CI {100*(1-alpha)}%)\n"
        else:
            warning += f"Control group appears normal (CI {100*(1-alpha)}%)\n"

        if p_value < alpha:
            warning += f"Test group is NOT from normal distribution (CI {100*(1-alpha)}%)\n"
        else:
            warning += f"Test group appears normal (CI {100*(1-alpha)}%)\n"
        result = {
            "n1": n1,
            "n2": n2,
            "stat": stat,
            "p": p_value,
            "var_test":var1,
            "var_control":var2,
            "mean_test":mean1,
            "mean_control":mean2,
            "effect": 1 if p_value<alpha else 0,
            "pearson":pearson,
            "spearman":spearman,
            "pearson_p":pearson_p,
            "spearman_p":spearman_p,
            "control_stat": control_stat,
            "control_p":control_p,
            "warning":warning
        }

        return Response(result), result
    except Exception as e:
        logging.error("Error while calculating")
        logging.exception(e)
        return HttpResponseBadRequest("Error while calculating", e.__str__()), None



def shapwilk_test(
    filepath_or_buffer,
    test_column,
    control_column,
    alpha,
    beta,
    related = False
):
    try:
        df = pd.read_csv(filepath_or_buffer=filepath_or_buffer)
        test = df[test_column]
        control = df[control_column]
        if test.empty or control.empty:
            raise ValueError("Error while extracting columns from the dataset")

        n1 = len(test)
        n2 = len(control)
        mean1, mean2 = test.mean(), control.mean()
        var1, var2 = test.var(ddof=1), control.var(ddof=1)
        
        pearson_obj = stats.pearsonr(test, control)
        spearman_obj = stats.spearmanr(test, control)

        pearson = pearson_obj[0]
        spearman = spearman_obj[0]

        pearson_p = pearson_obj[1]
        spearman_p = spearman_obj[1]

        result = stats.shapiro(test)
        result_control = stats.shapiro(control)
        stat, p_value = result[0], result[1]
        control_stat = result_control[0]
        control_p = result_control[1]
        warning = "Shapiro is not sensitive to outliers\n"
        if pearson_p < alpha:
            warning += f"Test and control may be dependent (Pearson={pearson:.2f})\n"
        if spearman_p < alpha:
            warning += f"Test and control may be dependent (Spearman={spearman:.2f})\n"
        if pearson_p >= alpha and spearman_p >= alpha:
            warning += "Test and control appear independent\n"
        if control_p < alpha:
            warning += f"Control group is NOT from normal distribution (CI {100*(1-alpha)}%)\n"
        else:
            warning += f"Control group appears normal (CI {100*(1-alpha)}%)\n"

        if p_value < alpha:
            warning += f"Test group is NOT from normal distribution (CI {100*(1-alpha)}%)\n"
        else:
            warning += f"Test group appears normal (CI {100*(1-alpha)}%)\n"
        result = {
            "n1": n1,
            "n2": n2,
            "stat": stat,
            "p": p_value,
            "var_test":var1,
            "var_control":var2,
            "mean_test":mean1,
            "mean_control":mean2,
            "effect": 1 if p_value<alpha else 0,
            "pearson":pearson,
            "spearman":spearman,
            "pearson_p":pearson_p,
            "spearman_p":spearman_p,
            "control_stat": control_stat,
            "control_p":control_p,
            "warning":warning
        }

        return Response(result), result
    except Exception as e:
        logging.error("Error while calculating")
        logging.exception(e)
        return HttpResponseBadRequest("Error while calculating", e.__str__()), None


def welch_test(
    filepath_or_buffer,
    test_column,
    control_column,
    alpha,
    beta,
    related = False
):
    try:
        df = pd.read_csv(filepath_or_buffer=filepath_or_buffer)
        test = df[test_column]
        control = df[control_column]
        if test.empty or control.empty:
            raise ValueError("Error while extracting columns from the dataset")

        n1 = len(test)
        n2 = len(control)
        mean1, mean2 = test.mean(), control.mean()
        var1, var2 = test.var(ddof=1), control.var(ddof=1)
        
        pearson_obj = stats.pearsonr(test, control)
        spearman_obj = stats.spearmanr(test, control)

        pearson = pearson_obj[0]
        spearman = spearman_obj[0]

        pearson_p = pearson_obj[1]
        spearman_p = spearman_obj[1]

        result = stats.shapiro(test)
        result_control = stats.ttest_ind(test, control, equal_var=False)
        stat, p_value = result[0], result[1]
        control_stat = result_control[0]
        control_p = result_control[1]
        warning = "Shapiro is not sensitive to outliers\n"
        if pearson_p < alpha:
            warning += f"Test and control may be dependent (Pearson={pearson:.2f})\n"
        if spearman_p < alpha:
            warning += f"Test and control may be dependent (Spearman={spearman:.2f})\n"
        if pearson_p >= alpha and spearman_p >= alpha:
            warning += "Test and control appear independent\n"
        if control_p < alpha:
            warning += f"Control group is NOT from normal distribution (CI {100*(1-alpha)}%)\n"
        else:
            warning += f"Control group appears normal (CI {100*(1-alpha)}%)\n"

        if p_value < alpha:
            warning += f"The differece is statistically important (CI {100*(1-alpha)}%)\n"
        else:
            warning += f"The differece is NOT statistically important (CI {100*(1-alpha)}%)\n"
        result = {
            "n1": n1,
            "n2": n2,
            "stat": stat,
            "p": p_value,
            "var_test":var1,
            "var_control":var2,
            "mean_test":mean1,
            "mean_control":mean2,
            "effect": 1 if p_value<alpha else 0,
            "pearson":pearson,
            "spearman":spearman,
            "pearson_p":pearson_p,
            "spearman_p":spearman_p,
            "control_stat": control_stat,
            "control_p":control_p,
            "warning":warning
        }

        return Response(result), result
    except Exception as e:
        logging.error("Error while calculating")
        logging.exception(e)
        return HttpResponseBadRequest("Error while calculating", e.__str__()), None



def anderson_darling_test(
    filepath_or_buffer,
    test_column,
    control_column,
    alpha,
    beta,
    related = False
):
    try:
        df = pd.read_csv(filepath_or_buffer=filepath_or_buffer)
        test = df[test_column]
        control = df[control_column]
        if test.empty or control.empty:
            raise ValueError("Error while extracting columns from the dataset")

        n1 = len(test)
        n2 = len(control)
        mean1, mean2 = test.mean(), control.mean()
        var1, var2 = test.var(ddof=1), control.var(ddof=1)
        
        pearson_obj = stats.pearsonr(test, control)
        spearman_obj = stats.spearmanr(test, control)

        pearson = pearson_obj[0]
        spearman = spearman_obj[0]

        pearson_p = pearson_obj[1]
        spearman_p = spearman_obj[1]

        from statsmodels.stats.diagnostic import lilliefors
        result = stats.anderson(test)
        result_control = stats.anderson(control)
        stat, p_value = result[0], result[1]
        control_stat = result_control[0]
        control_p = result_control[1]
        warning = "Anderson-Darling test can be sensitive to the outliers, try using Shapiro-Wilke test too\n"
        if pearson_p < alpha:
            warning += f"Test and control may be dependent (Pearson={pearson:.2f})\n"
        if spearman_p < alpha:
            warning += f"Test and control may be dependent (Spearman={spearman:.2f})\n"
        if pearson_p >= alpha and spearman_p >= alpha:
            warning += "Test and control appear independent\n"
        if control_p < alpha:
            warning += f"Control group is NOT from normal distribution (CI {100*(1-alpha)}%)\n"
        else:
            warning += f"Control group appears normal (CI {100*(1-alpha)}%)\n"

        if p_value < alpha:
            warning += f"Test group is NOT from normal distribution (CI {100*(1-alpha)}%)\n"
        else:
            warning += f"Test group appears normal (CI {100*(1-alpha)}%)\n"
        result = {
            "n1": n1,
            "n2": n2,
            "stat": stat,
            "p": p_value,
            "var_test":var1,
            "var_control":var2,
            "mean_test":mean1,
            "mean_control":mean2,
            "effect": 1 if p_value<alpha else 0,
            "pearson":pearson,
            "spearman":spearman,
            "pearson_p":pearson_p,
            "spearman_p":spearman_p,
            "control_stat": control_stat,
            "control_p":control_p,
            "warning":warning
        }

        return Response(result), result
    except Exception as e:
        logging.error("Error while calculating")
        logging.exception(e)
        return HttpResponseBadRequest("Error while calculating", e.__str__()), None



def anova(
    filepath_or_buffer,
    test_column,
    control_column,
    alpha,
    beta,
    related = False
):
    try:
        df = pd.read_csv(filepath_or_buffer=filepath_or_buffer)
        test = df[test_column]
        control = df[control_column]
        if test.empty or control.empty:
            raise ValueError("Error while extracting columns from the dataset")

        n1 = len(test)
        n2 = len(control)
        mean1, mean2 = test.mean(), control.mean()
        var1, var2 = test.var(ddof=1), control.var(ddof=1)
        
        
        leven_stat, leven_pvalue = stats.levene(test, control)

        pearson_obj = stats.pearsonr(test, control)
        spearman_obj = stats.spearmanr(test, control)

        pearson = pearson_obj[0]
        spearman = spearman_obj[0]

        pearson_p = pearson_obj[1]
        spearman_p = spearman_obj[1]
        warning = "ANOVA requires the gomogenisis of variances, independancy and normal distribution in the groups\n"

        if leven_pvalue>0.05:
            result = stats.f_oneway(test, control)
            stat, p_value = result[0], result[1]
        else:
            warning += "The distributions have geterogenic variances, you should not use ANOVA then"
            stat, p_value = 0, 1
        if pearson_p < alpha:
            warning += f"Test and control may be dependent (Pearson={pearson:.2f})\n"
        if spearman_p < alpha:
            warning += f"Test and control may be dependent (Spearman={spearman:.2f})\n"
        if pearson_p >= alpha and spearman_p >= alpha:
            warning += "Test and control appear independent\n"

        if p_value < alpha:
            warning += f"The differece is statistically important (CI {100*(1-alpha)}%)\n"
        else:
            warning += f"The differece is NOT statistically important (CI {100*(1-alpha)}%)\n"
        result = {
            "n1": n1,
            "n2": n2,
            "stat": stat,
            "p": p_value,
            "var_test":var1,
            "var_control":var2,
            "mean_test":mean1,
            "mean_control":mean2,
            "effect": 1 if p_value<alpha else 0,
            "pearson":pearson,
            "spearman":spearman,
            "pearson_p":pearson_p,
            "spearman_p":spearman_p,
            "warning":warning
        }

        return Response(result), result
    except Exception as e:
        logging.error("Error while calculating")
        logging.exception(e)
        return HttpResponseBadRequest("Error while calculating", e.__str__()), None


def cuped(
    filepath_or_buffer,
    test_column,
    control_column,
    history_buf,
    history_col,
    alpha,
    beta,
):
    try:
        history_df = pd.read_csv(history_buf)
        if history_col in history_df.columns:
            hist_series = history_df[history_col]
        else:
            hist_series = history_df.iloc[:, 0]
        if hist_series is None or hist_series.empty:
            raise ValueError("Историческая колонка пуста")

        df = pd.read_csv(filepath_or_buffer=filepath_or_buffer)
        test = df[test_column]
        control = df[control_column]
        if test.empty or control.empty:
            raise ValueError("Error while extracting columns from the dataset")

        theta = np.cov(pd.concat((test, control), axis=0), hist_series)[0, 1]/np.var(hist_series, ddof=1)
        if len(test) != len(control) or len(control) != len(hist_series):
            min_length = min(len(control), len(test), len(hist_series))
            test = test.iloc[:min_length]
            control = control.iloc[:min_length]
            hist_series = hist_series.iloc[:min_length]
            df = df.iloc[:min_length]
        hist_mean = hist_series.mean()
        test_cuped = test - theta*(hist_series - hist_mean)
        control_cuped = control - theta*(hist_series - hist_mean)
        df[test_column] = test_cuped
        df[control_column] = control_cuped
        return df
    except Exception as e:
        logging.error("Error while calculating")
        logging.exception(e)
        return None


def bootstrap(
    filepath_or_buffer,
    test_column,
    control_column,
    alpha=0.05,
    beta=0.2,
    iterations = 10000,
    related = False
):
    try:
        df = pd.read_csv(filepath_or_buffer=filepath_or_buffer)
        test = df[test_column]
        control = df[control_column]
        if test.empty or control.empty:
            raise ValueError("Error while extracting columns from the dataset")

        n1 = len(test)
        n2 = len(control)
        mean1, mean2 = test.mean(), control.mean()
        var1, var2 = test.var(ddof=1), control.var(ddof=1)
        
        pearson_obj = stats.pearsonr(test, control)
        spearman_obj = stats.spearmanr(test, control)

        pearson = pearson_obj[0]
        spearman = spearman_obj[0]

        pearson_p = pearson_obj[1]
        spearman_p = spearman_obj[1]


        boot_diffs = []
        for _ in range(iterations):
            t_sample = np.random.choice(test, size=len(test), replace=True)
            c_sample = np.random.choice(control, size=len(control), replace=True)
            boot_diffs.append(np.mean(t_sample) - np.mean(c_sample))

        ci = np.percentile(boot_diffs, [2.5, 97.5])
        effect = ""
        if 0 > ci[0] and 0 < ci[1]:
            effect = False
        else:
            effect = True

        warning = "Bootstrap is a very expensive method, it can take a while to finish the calculations. \n\n Bootstrap results can be unpredictable if the sample is non-representative, or the sample has N<10\n"
        if pearson_p < alpha:
            warning += f"Test and control may be dependent (Pearson={pearson:.2f})\n"
        if spearman_p < alpha:
            warning += f"Test and control may be dependent (Spearman={spearman:.2f})\n"
        if pearson_p >= alpha and spearman_p >= alpha:
            warning += "Test and control appear independent\n"

        result = {
            "n1": n1,
            "n2": n2,
            "ci": ci,
            "var_test":var1,
            "var_control":var2,
            "mean_test":mean1,
            "mean_control":mean2,
            "effect": effect,
            "pearson":pearson,
            "spearman":spearman,
            "pearson_p":pearson_p,
            "spearman_p":spearman_p,
            "warning":warning
        }

        return Response(result), result
    except Exception as e:
        logging.error("Error while calculating")
        logging.exception(e)
        return HttpResponseBadRequest("Error while calculating", e.__str__()), None
