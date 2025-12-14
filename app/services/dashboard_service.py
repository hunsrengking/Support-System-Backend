from sqlalchemy.orm import Session
from sqlalchemy import text


def get_summary(db: Session):
    total_tickets = db.execute(text("SELECT COUNT(*) FROM tickets")).scalar()
    total_tickets_today = db.execute(
        text(
            "SELECT COUNT(*) FROM tickets WHERE create_date >= CURDATE() AND create_date < CURDATE() + INTERVAL 1 DAY"
        )
    ).scalar()
    total_tickets_Resolved = db.execute(
        text("SELECT COUNT(*) FROM tickets WHERE status_id = 6")
    ).scalar()
    total_tickets_Open = db.execute(
        text("SELECT COUNT(*) FROM tickets WHERE status_id = 3")
    ).scalar()
    total_tickets_Wating_approve = db.execute(
        text("SELECT COUNT(*) FROM tickets WHERE status_id = 8")
    ).scalar()

    return {
        "totalTickets": total_tickets,
        "totalTicketstoday": total_tickets_today,
        "totalTicketsResolved": total_tickets_Resolved,
        "totalTicketsopen": total_tickets_Open,
        "totalTicketswatingapprove": total_tickets_Wating_approve,
    }


def tickets_by_date(db: Session):
    return (
        db.execute(
            text(
                """
            SELECT 
              DATE(create_date) AS day,
              COUNT(*) AS total
            FROM tickets
            WHERE create_date >= CURDATE() - INTERVAL 6 DAY
            GROUP BY DATE(create_date)
            ORDER BY day
        """
            )
        )
        .mappings()
        .all()
    )


def tickets_by_month(db: Session):
    return (
        db.execute(
            text(
                """
            WITH RECURSIVE months AS (
                SELECT 
                    DATE_FORMAT(
                    DATE_SUB(CURDATE(), INTERVAL 11 MONTH),
                    '%Y-%m-01'
                    ) AS first_day
                UNION ALL
                SELECT 
                    DATE_FORMAT(
                    DATE_ADD(first_day, INTERVAL 1 MONTH),
                    '%Y-%m-01'
                    )
                FROM months
                WHERE first_day < DATE_FORMAT(CURDATE(), '%Y-%m-01')
                )
                SELECT 
                DATE_FORMAT(m.first_day, '%Y-%m') AS month,
                COALESCE(COUNT(t.id), 0) AS total
                FROM months m
                LEFT JOIN tickets t
                ON t.create_date >= m.first_day
                AND t.create_date <  DATE_ADD(m.first_day, INTERVAL 1 MONTH)
                GROUP BY m.first_day
                ORDER BY m.first_day;

        """
            )
        )
        .mappings()
        .all()
    )
