from os import name
from typing import Dict, List
import pandas as pd
import numpy as np
import scipy.stats as stats
import seaborn as sns
import zipfile
import io
import matplotlib as mplb
mplb.use('Agg')
import matplotlib.pyplot as plt
import logging
from pprint import pprint
from django.http.response import HttpResponseBadRequest, HttpResponse
from rest_framework.response import Response
import json
from django.forms.models import model_to_dict

from api.models import Distribution


distribution_map = {
    "normal": stats.norm,
    "binomial": stats.binom,
    "poisson": stats.poisson,
    "uniform": stats.uniform,
    "exponential": stats.expon,
    "beta": stats.beta,
    "gamma": stats.gamma,
    "lognormal": stats.lognorm,
    "chi2": stats.chi2,
    "t": stats.t,
    "f": stats.f,
    "geometric": stats.geom,
    "hypergeom": stats.hypergeom,
    "negative_binomial": stats.nbinom
}


discrete_distributions = (
    "binomial",
    "poisson",
    "geometric",
    "hypergeom",
    "negative_binomial"
)

def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

param_transform_map = {
    "normal": lambda p: {
        "loc": safe_float(p.get("mu", 0)),
        "scale": safe_float(p.get("sigma", 1))
    },
    "binomial": lambda p: {
        "n": safe_int(p.get("n", 10)),
        "p": safe_float(p.get("p", 0.5))
    },
    "poisson": lambda p: {
        "mu": safe_float(p.get("mu", 1))
    },
    "uniform": lambda p: {
        "loc": safe_float(p.get("a", 0)),
        "scale": safe_float(p.get("b", 1)) - safe_float(p.get("a", 0))
    },
    "exponential": lambda p: {
        "scale": 1.0 / safe_float(p.get("lambda", 1))
    },
    "beta": lambda p: {
        "a": safe_float(p.get("a", 2)),
        "b": safe_float(p.get("b", 2))
    },
    "gamma": lambda p: {
        "a": safe_float(p.get("alpha", 2)),
        "scale": safe_float(p.get("beta", 2))
    },
    "lognormal": lambda p: {
        "s": safe_float(p.get("sigma", 1)),
        "scale": np.exp(safe_float(p.get("mu", 0)))
    },
    "chi2": lambda p: {
        "df": safe_float(p.get("df", 2))
    },
    "t": lambda p: {
        "df": safe_float(p.get("df", 10))
    },
    "f": lambda p: {
        "dfn": safe_float(p.get("dfn", 5)),
        "dfd": safe_float(p.get("dfd", 2))
    },
    "geometric": lambda p: {
        "p": safe_float(p.get("p", 0.5))
    },
    "hypergeom": lambda p: {
        "M": safe_int(p.get("M", 20)),
        "n": safe_int(p.get("n", 7)),
        "N": safe_int(p.get("N", 12))
    },
    "negative_binomial": lambda p: {
        "n": safe_int(p.get("n", 10)),
        "p": safe_float(p.get("p", 0.5))
    },
}


def plot_distribution(distribution):
    try:
        dist_name = distribution.get("name")
        dist_params = distribution.get("distribution_parameters")
        dist_type = distribution.get("distribution_type")

        if not dist_name or not dist_params or not dist_type:
            raise ValueError("Invalid or empty data given")

        dist_params = json.loads(dist_params)

        if not distribution:
            raise ValueError("Invalid distribution given")

        dist_class = distribution_map.get(dist_type)
        if not dist_class:
            raise ValueError(f"Unknown distribution: {dist_type}")

        if dist_type in param_transform_map:
            dist_kwargs = param_transform_map[dist_type](dist_params)
        else:
            dist_kwargs = dist_params

        dist = dist_class(**dist_kwargs)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            plt.figure(figsize=(8, 6))
            if dist_type in discrete_distributions:
                lower = int(dist.ppf(0.001))
                upper = int(dist.ppf(0.999)) + 1
                x = np.arange(lower, upper)

                pmf_values = dist.pmf(x)
                cdf_values = dist.cdf(x)
                plt.xlim((lower, upper))
                plt.bar(x, pmf_values, color='blue', alpha=0.6, label="PMF")
                plt.plot(x, cdf_values, 'r-o', label="CDF")
            else:
                x = np.linspace(dist.ppf(0.001), dist.ppf(0.999), 1000)
                pdf_values = dist.pdf(x)
                cdf_values = dist.cdf(x)

                plt.plot(x, pdf_values, label="PDF")
                plt.plot(x, cdf_values, label="CDF")

            plt.title(f"{dist_name} distribution")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.axhline(0, color='black', linewidth=0.5)
            plt.axvline(0, color='black', linewidth=0.5)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300)
            plt.close()
            buf.seek(0)
            zipf.writestr(f"{dist_name}.png", buf.getvalue())

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="report_bundle.zip"'
        return response, zip_buffer.getvalue()

    except Exception as e:
        logging.exception(f"Ошибка в plot_distribution: {e}")
        return Response({"error": str(e)}, status=400), str(e)


def get_probability(distribution, a):
    try:
        dist_name = distribution.get("name")
        dist_params = distribution.get("distribution_parameters")
        dist_type = distribution.get("distribution_type")

        if not dist_name or not dist_params or not dist_type or a is None:
            raise ValueError("Invalid or empty data given")

        dist_params = json.loads(dist_params)

        if not distribution:
            raise ValueError("Invalid distribution given")

        dist_class = distribution_map.get(dist_type)
        if not dist_class:
            raise ValueError(f"Unknown distribution: {dist_type}")

        if dist_type in param_transform_map:
            dist_kwargs = param_transform_map[dist_type](dist_params)
        else:
            dist_kwargs = dist_params

        dist = dist_class(**dist_kwargs)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            plt.figure(figsize=(8, 6))
            if dist_type in discrete_distributions:
                lower = int(dist.ppf(0.001))
                upper = int(dist.ppf(0.999)) + 1
                x = np.arange(lower, upper)

                pmf_values = dist.pmf(x)
                cdf_values = dist.cdf(x)
                plt.xlim((lower, upper))
                plt.bar(x, pmf_values, color='blue', alpha=0.6, label="PMF")
                plt.bar(x[x<=a], pmf_values[x<=a], color='orange', alpha=0.8, label=f"P(X≤{a})")
                plt.plot(x, cdf_values, 'r-o', label="CDF")
            else:
                x = np.linspace(dist.ppf(0.001), dist.ppf(0.999), 1000)
                pdf_values = dist.pdf(x)
                cdf_values = dist.cdf(x)
                plt.fill_between(x, 0, pdf_values, where=(x<=a), color='orange', alpha=0.5, label=f"P(X≤{a})")
                plt.plot(x, pdf_values, label="PDF")
                plt.plot(x, cdf_values, label="CDF")
            plt.axvline(x=a, color='red', linestyle='--', linewidth=2, label='a value')
            plt.axhline(y=dist.cdf(a), color='red', linestyle='--', linewidth=2, label=f"P(x<={a}) = {dist.cdf(a)}")

            plt.title(f"P(x<={a}) = {dist.cdf(a)}")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.axhline(0, color='black', linewidth=0.5)
            plt.axvline(0, color='black', linewidth=0.5)
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300)
            plt.close()
            buf.seek(0)
            zipf.writestr(f"{dist_name}.png", buf.getvalue())

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="report_bundle.zip"'
        return response, zip_buffer.getvalue()

    except Exception as e:
        logging.exception(f"Ошибка в plot_distribution: {e}")
        return Response({"error": str(e)}, status=400), str(e)


def get_interval(distribution, a, b):
    try:
        dist_name = distribution.get("name")
        dist_params = distribution.get("distribution_parameters")
        dist_type = distribution.get("distribution_type")

        if not dist_name or not dist_params or not dist_type or a is None or b is None:
            raise ValueError("Invalid or empty data given")

        dist_params = json.loads(dist_params)
        dist_class = distribution_map.get(dist_type)
        if not dist_class:
            raise ValueError(f"Unknown distribution: {dist_type}")

        dist_kwargs = param_transform_map.get(dist_type, lambda p: p)(dist_params)
        dist = dist_class(**dist_kwargs)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            plt.figure(figsize=(8, 6))

            if dist_type in discrete_distributions:
                lower = int(dist.ppf(0.001))
                upper = int(dist.ppf(0.999)) + 1
                x = np.arange(lower, upper)
                pmf_values = dist.pmf(x)
                plt.bar(x, pmf_values, color='blue', alpha=0.6, label="PMF")
                
                mask = (x >= a) & (x <= b)
                plt.bar(x[mask], pmf_values[mask], color='orange', alpha=0.8, label=f"P({a}≤X≤{b})")
                
                p_interval = dist.cdf(b) - dist.cdf(a-1)
                plt.title(f"P({a}≤X≤{b}) = {p_interval:.4f}")

            else:
                x = np.linspace(dist.ppf(0.001), dist.ppf(0.999), 1000)
                pdf_values = dist.pdf(x)
                plt.plot(x, pdf_values, label="PDF")
                
                mask = (x >= a) & (x <= b)
                plt.fill_between(x[mask], 0, pdf_values[mask], color='orange', alpha=0.5, label=f"P({a}≤X≤{b})")
                
                p_interval = dist.cdf(b) - dist.cdf(a)
                plt.title(f"P({a}≤X≤{b}) = {p_interval:.4f}")


            plt.axvline(a, color='red', linestyle='--', linewidth=2)
            plt.axvline(b, color='red', linestyle='--', linewidth=2)

            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.axhline(0, color='black', linewidth=0.5)
            plt.axvline(0, color='black', linewidth=0.5)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300)
            plt.close()
            buf.seek(0)
            zipf.writestr(f"{dist_name}.png", buf.getvalue())

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="report_bundle.zip"'
        return response, zip_buffer.getvalue()

    except Exception as e:
        logging.exception(f"Ошибка в get_interval: {e}")
        return Response({"error": str(e)}, status=400), str(e)


def get_quantile(distribution, quantile):
    try:
        dist_name = distribution.get("name")
        dist_params = distribution.get("distribution_parameters")
        dist_type = distribution.get("distribution_type")

        if not dist_name or not dist_params or not dist_type:
            raise ValueError("Invalid or empty data given")

        dist_params = json.loads(dist_params)
        dist_class = distribution_map.get(dist_type)
        if not dist_class:
            raise ValueError(f"Unknown distribution: {dist_type}")

        dist_kwargs = param_transform_map.get(dist_type, lambda p: p)(dist_params)
        dist = dist_class(**dist_kwargs)


        a = dist.ppf(quantile)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            plt.figure(figsize=(9, 6))

            if dist_type in discrete_distributions:
                lower, upper = int(dist.ppf(0.001)), int(dist.ppf(0.999)) + 1
                x = np.arange(lower, upper)
                pmf_values = dist.pmf(x)
                cdf_values = dist.cdf(x)

                plt.bar(x, pmf_values, color="#6baed6", alpha=0.6, label="PMF")
                plt.bar(x[x<=a], pmf_values[x<=a], color="#fd8d3c", alpha=0.8, label=f"P(X≤{a:.2f})")
                plt.plot(x, cdf_values, 'r-o', label="CDF", markersize=4)

            else:
                x = np.linspace(dist.ppf(0.001), dist.ppf(0.999), 1000)
                pdf_values = dist.pdf(x)
                cdf_values = dist.cdf(x)

                plt.plot(x, pdf_values, color="#6baed6", label="PDF", linewidth=2)
                plt.plot(x, cdf_values, color="#fd8d3c", label="CDF", linewidth=2)
                plt.fill_between(x, 0, pdf_values, where=(x <= a), color="#fd8d3c", alpha=0.3, label=f"P(X≤{a:.2f})")


            plt.axvline(x=a, color='black', linestyle='--', linewidth=1.5)
            plt.annotate(f'{a:.2f}', xy=(a, 0), xytext=(a, max(pdf_values)*0.05),
                         arrowprops=dict(arrowstyle='->', color='black'), ha='center')

            plt.title(f"{dist_name} distribution: quantile {quantile*100:.1f}% = {a:.2f}", fontsize=14)
            plt.xlabel("X")
            plt.ylabel("Probability")
            plt.legend()
            plt.grid(alpha=0.3)
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300)
            plt.close()
            buf.seek(0)
            zipf.writestr(f"{dist_name}_quantile.png", buf.getvalue())

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="quantile_report.zip"'
        return response, zip_buffer.getvalue()

    except Exception as e:
        logging.exception(f"Ошибка в get_quantile: {e}")
        return Response({"error": str(e)}, status=400), str(e)


def get_sample(distribution, n):
    try:
        dist_name = distribution.get("name")
        dist_params = distribution.get("distribution_parameters")
        dist_type = distribution.get("distribution_type")

        if not dist_name or not dist_params or not dist_type:
            raise ValueError("Invalid or empty data given")

        dist_params = json.loads(dist_params)
        dist_class = distribution_map.get(dist_type)
        if not dist_class:
            raise ValueError(f"Unknown distribution: {dist_type}")

        dist_kwargs = param_transform_map.get(dist_type, lambda p: p)(dist_params)
        dist = dist_class(**dist_kwargs)

        sample = dist.rvs(size=n)


        df = pd.DataFrame({
            "sample": sample
        })

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sample')

        excel_buffer.seek(0)
        response = HttpResponse(
            excel_buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{dist_name}_sample.xlsx"'

        return response, excel_buffer.read()

    except Exception as e:
        logging.exception(f"Ошибка в get_sample_excel: {e}")
        return HttpResponse(
            json.dumps({"error": str(e)}),
            content_type='application/json',
            status=400
        )