import { type ButtonHTMLAttributes, type InputHTMLAttributes, type ReactNode } from 'react';
import clsx from 'clsx';

export const Button = ({ className, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) => (
  <button
    className={clsx(
      'rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-primary-700',
      className
    )}
    {...props}
  />
);

export const Input = ({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) => (
  <input
    className={clsx(
      'w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none ring-primary-500 focus:ring-2',
      className
    )}
    {...props}
  />
);

export const Card = ({ children, className }: { children: ReactNode; className?: string }) => (
  <div className={clsx('rounded-lg border border-slate-200 bg-white p-4 shadow-sm', className)}>{children}</div>
);

export const Loader = ({ label = 'Loading...' }: { label?: string }) => (
  <div className="flex items-center justify-center p-6 text-sm text-slate-500">{label}</div>
);

export const ErrorBox = ({ message }: { message?: string }) =>
  message ? <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-600">{message}</div> : null;

export const Modal = ({
  title,
  open,
  onClose,
  children
}: {
  title: string;
  open: boolean;
  onClose: () => void;
  children: ReactNode;
}) => {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4" onClick={onClose}>
      <div className="w-full max-w-lg rounded-xl bg-white p-6" onClick={(e) => e.stopPropagation()}>
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold">{title}</h3>
          <button className="text-slate-500" onClick={onClose} type="button">
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  );
};
