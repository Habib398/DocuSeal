import React, { useEffect } from 'react';

export interface Alert {
  id: string;
  type: 'success' | 'danger' | 'warning' | 'info';
  message: string;
}

interface AlertsProps {
  alerts: Alert[];
  onDismiss: (id: string) => void;
}

const Alerts: React.FC<AlertsProps> = ({ alerts, onDismiss }) => {
  useEffect(() => {
    // Desaparecer alerta después de 5 segundos
    alerts.forEach((alert) => {
      const timer = setTimeout(() => {
        onDismiss(alert.id);
      }, 5000);

      return () => clearTimeout(timer);
    });
  }, [alerts, onDismiss]);

  return (
    <div id="alerts" className="position-fixed end-0 top-0 p-3" style={{ zIndex: 1080, maxWidth: '380px' }}>
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className={`alert alert-${alert.type} alert-dismissible fade show fade-in`}
          role="alert"
        >
          {alert.message}
          <button
            type="button"
            className="btn-close"
            onClick={() => onDismiss(alert.id)}
            aria-label="Close"
          ></button>
        </div>
      ))}
    </div>
  );
};

export default Alerts;
