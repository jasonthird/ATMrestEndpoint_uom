from fastapi import FastAPI
from pydantic import BaseModel
from decimal import Decimal

from clientLib import Atm

app = FastAPI()

AtmHost = "localhost"
AtmPort = 5672


class AuthResponse(BaseModel):
    success: bool
    token: str


class AuthRequest(BaseModel):
    username: str
    pin: str


class BalanceResponse(BaseModel):
    success: bool
    balance: Decimal


class BalanceRequest(BaseModel):
    token: str


class PatchBalanceRequest(BaseModel):
    token: str
    amount: Decimal


class PatchBalanceResponse(BaseModel):
    deposited: Decimal
    withdrawn: Decimal


@app.post("/atm/auth", response_model=AuthResponse)
async def auth(request: AuthRequest):
    try:
        atm = Atm(AtmHost, AtmPort)
        atmResponse = atm.auth(request.username, request.pin)
        if atmResponse == "False":
            return AuthResponse(success=False, token="")
        else:
            return AuthResponse(success=True, token=atmResponse)
    except Exception as e:
        return AuthResponse(success=False, token="")
    finally:
        atm.close()


@app.get("/atm/balance", response_model=BalanceResponse)
async def balance(request: BalanceRequest):
    try:
        atm = Atm(AtmHost, AtmPort)
        atmResponse = atm.balance(request.token)
        if atmResponse == "False":
            return BalanceResponse(success=False, balance="")
        else:
            return BalanceResponse(success=True, balance=atmResponse)
    except Exception as e:
        return BalanceResponse(success=False, balance="")
    finally:
        atm.close()


@app.patch("/atm/balance", response_model=PatchBalanceResponse)
async def change(request: PatchBalanceRequest):
    try:
        atm = Atm(AtmHost, AtmPort)
        money = Decimal(request.amount)
        if money < 0:
            atmResponse = atm.withdraw(request.token, str(money * -1))
            return PatchBalanceResponse(deposited=0, withdrawn=atmResponse)
        else:
            atmResponse = atm.deposit(request.token, str(money))
            return PatchBalanceResponse(deposited=atmResponse, withdrawn=0)
    except Exception as e:
        return PatchBalanceResponse(deposited=0, withdrawn=0)
    finally:
        atm.close()

