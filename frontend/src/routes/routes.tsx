import { type RouteObject } from "react-router-dom";
import App from "../App";
import ProtectedRoute from "../components/ProtectedRoute";
import DashboardPage from "../pages/DashboardPage";
import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";
import PatientsPage from "../pages/PatientsPage";
import StrokePage from "../pages/StrokePage";
import UploadReportPage from "../pages/UploadReportPage";
import DrugSafetyPage from "../pages/DrugSafetyPage";
import KnowledgePage from "../pages/KnowledgePage";
import ChatPage from "../pages/ChatPage";
import ReportsPage from "../pages/ReportsPage";
import NotFoundPage from "../pages/NotFoundPage";

export const routes: RouteObject[] = [
  {
    path: "/",
    element: <App />,
    children: [
      { path: "login", element: <LoginPage /> },
      { path: "register", element: <RegisterPage /> },
      {
        element: <ProtectedRoute />,
        children: [
          { index: true, element: <DashboardPage /> },
          { path: "patients", element: <PatientsPage /> },
          { path: "stroke", element: <StrokePage /> },
          { path: "upload-report", element: <UploadReportPage /> },
          { path: "drug-safety", element: <DrugSafetyPage /> },
          { path: "knowledge", element: <KnowledgePage /> },
          { path: "chat", element: <ChatPage /> },
          { path: "reports", element: <ReportsPage /> },
        ],
      },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
];
