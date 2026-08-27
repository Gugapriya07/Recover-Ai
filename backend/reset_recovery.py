from database import SessionLocal
from models import RecoveryLog, RecoveryAttempt, Transaction, Customer


db = SessionLocal()

try:

    # =========================================================
    # 1. DELETE RECOVERY HISTORY
    # =========================================================

    db.query(RecoveryLog).delete()

    # =========================================================
    # 2. DELETE RECOVERY ATTEMPTS
    # =========================================================

    db.query(RecoveryAttempt).delete()

    # =========================================================
    # 3. DELETE ALL TRANSACTIONS
    # =========================================================

    db.query(Transaction).delete()

    # =========================================================
    # 4. DELETE ALL CUSTOMERS
    # =========================================================

    db.query(Customer).delete()

    # =========================================================
    # 5. RESET DATABASE
    # =========================================================

    db.commit()

    print("======================================")
    print("RECOVERAI DATABASE RESET SUCCESSFUL")
    print("======================================")
    print("Recovery logs     : CLEARED")
    print("Recovery attempts : CLEARED")
    print("Transactions      : CLEARED")
    print("Customers         : CLEARED")
    print("======================================")
    print("Now run: python seed_data.py")


except Exception as e:

    db.rollback()

    print("======================================")
    print("RESET FAILED")
    print("====================python reset_recovery.py==================")
    print(e)


finally:

    db.close()