#!/usr/bin/env python3
"""
CLI de teste para ExchangeService - chama os metodos reais da classe.

Requer .env configurado com AIRTABLE_TOKEN, AIRTABLE_BASE_URL, etc.

Uso:
  python exchange_cli.py list_all
  python exchange_cli.py sync_all
  python exchange_cli.py fetch <CODE> <CODEIN>
  python exchange_cli.py sync_exchange <CODE> <CODEIN> --currency-id <ID> [--exchange-id <ID>]

Exemplos:
  python exchange_cli.py list_all
  python exchange_cli.py sync_all
  python exchange_cli.py fetch USD BRL
  python exchange_cli.py fetch EUR BRL
  python exchange_cli.py sync_exchange USD BRL --currency-id recFTu2BE9PnKgJ4u
  python exchange_cli.py sync_exchange USD BRL --currency-id recFTu2BE9PnKgJ4u --exchange-id recov2d7ZkAekb9AM
"""

import os

# DATABASE_URL e SECRET_KEY sao obrigatorios no Settings mas nao sao usados
# pelo ExchangeService. Definimos defaults para que o CLI funcione sem .env completo.
os.environ.setdefault("DATABASE_URL", "sqlite:///unused-by-exchange-cli")
os.environ.setdefault("SECRET_KEY", "unused-by-exchange-cli")

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone

from app.schemas.currency import CurrencyResponse
from app.services.exchange_service import ExchangeService


def _print_separator():
    print("-" * 60)


def _print_result(titulo: str, resultado):
    print()
    _print_separator()
    print(f"  {titulo}")
    _print_separator()
    if isinstance(resultado, (dict, list)):
        print(json.dumps(resultado, indent=2, default=str))
    else:
        print(resultado)
    print()


def _print_header(comando: str, **kwargs):
    print()
    _print_separator()
    print(f"  Comando : {comando}")
    for k, v in kwargs.items():
        print(f"  {k:<9}: {v}")
    print(f"  Hora    : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    _print_separator()


class ExchangeServiceCLI:

    # ── list_all ──────────────────────────────────────────────

    async def cmd_list_all(self):
        _print_header("list_all()")
        service = ExchangeService()
        try:
            result = await service.list_all()
            _print_result(
                f"Sucesso - {len(result)} registro(s)",
                [r.model_dump() for r in result],
            )
        except Exception as exc:
            _print_result("Erro", {"tipo": type(exc).__name__, "mensagem": str(exc)})
            sys.exit(1)

    # ── sync_all ──────────────────────────────────────────────

    async def cmd_sync_all(self):
        _print_header("sync_all()")
        service = ExchangeService()
        try:
            result = await service.sync_all()
            _print_result("Resultado", result)
        except Exception as exc:
            _print_result("Erro", {"tipo": type(exc).__name__, "mensagem": str(exc)})
            sys.exit(1)

    # ── _fetch_awesome_api ────────────────────────────────────

    async def cmd_fetch(self, code: str, codein: str):
        _print_header("_fetch_awesome_api()", code=code, codein=codein)
        service = ExchangeService()
        try:
            result = await service._fetch_awesome_api(code, codein)
            _print_result("Cotacao recebida", result)
        except Exception as exc:
            _print_result("Erro", {"tipo": type(exc).__name__, "mensagem": str(exc)})
            sys.exit(1)

    # ── _sync_exchange ────────────────────────────────────────

    async def cmd_sync_exchange(
        self,
        code: str,
        codein: str,
        currency_id: str,
        exchange_id: str | None,
    ):
        operacao = f"PUT (atualizar {exchange_id})" if exchange_id else "POST (criar novo)"
        _print_header(
            "_sync_exchange()",
            code=code,
            codein=codein,
            currency_id=currency_id,
            exchange_id=exchange_id or "(nenhum)",
            operacao=operacao,
        )

        service = ExchangeService()

        print("  [1/2] Buscando cotacao na AwesomeAPI...")
        try:
            quote = await service._fetch_awesome_api(code, codein)
        except Exception as exc:
            _print_result(
                "Erro ao buscar cotacao",
                {"tipo": type(exc).__name__, "mensagem": str(exc)},
            )
            sys.exit(1)

        print(f"  Quote obtida: {quote}\n")

        currency = CurrencyResponse(
            id=currency_id,
            name=f"{code}_{codein}",
            code=code,
            codein=codein,
            last_date=datetime.now(timezone.utc),
            exchange=exchange_id,
        )

        print("  [2/2] Sincronizando com Airtable...")
        try:
            result = await service._sync_exchange(currency, quote)
            _print_result("Resultado", result)
        except Exception as exc:
            _print_result("Erro", {"tipo": type(exc).__name__, "mensagem": str(exc)})
            sys.exit(1)

    # ── entry point ───────────────────────────────────────────

    def run(self):
        parser = argparse.ArgumentParser(
            description="CLI de teste para ExchangeService (chamadas reais)",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=__doc__,
        )

        sub = parser.add_subparsers(dest="comando", required=True)

        sub.add_parser("list_all", help="Chama ExchangeService.list_all()")

        sub.add_parser("sync_all", help="Chama ExchangeService.sync_all()")

        p_fetch = sub.add_parser("fetch", help="Chama ExchangeService._fetch_awesome_api()")
        p_fetch.add_argument("code", help="Moeda origem  ex: USD")
        p_fetch.add_argument("codein", help="Moeda destino ex: BRL")

        p_sync = sub.add_parser("sync_exchange", help="Chama ExchangeService._sync_exchange()")
        p_sync.add_argument("code", help="Moeda origem  ex: USD")
        p_sync.add_argument("codein", help="Moeda destino ex: BRL")
        p_sync.add_argument(
            "--currency-id",
            required=True,
            metavar="ID",
            help="Airtable record ID da Currency (ex: recFTu2BE9PnKgJ4u)",
        )
        p_sync.add_argument(
            "--exchange-id",
            default=None,
            metavar="ID",
            help="Airtable record ID do Exchange existente - omitir para criar novo (POST)",
        )

        args = parser.parse_args()

        if args.comando == "list_all":
            asyncio.run(self.cmd_list_all())
        elif args.comando == "sync_all":
            asyncio.run(self.cmd_sync_all())
        elif args.comando == "fetch":
            asyncio.run(self.cmd_fetch(args.code, args.codein))
        elif args.comando == "sync_exchange":
            asyncio.run(
                self.cmd_sync_exchange(
                    args.code,
                    args.codein,
                    currency_id=args.currency_id,
                    exchange_id=args.exchange_id,
                )
            )


if __name__ == "__main__":
    ExchangeServiceCLI().run()
