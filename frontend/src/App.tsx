import { Outlet, useLocation } from "react-router-dom";
import AppShell from "./layouts/AppShell";

function App() {
  const location = useLocation();
  const isPublicRoute = location.pathname === "/login" || location.pathname === "/register";

  if (isPublicRoute) {
    return <Outlet />;
  }

  return (
    <AppShell>
      <Outlet />
    </AppShell>
  );
}

export default App;
