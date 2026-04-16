import Navbar from "./components/Navbar.tsx";
import { useAuth } from "./Context.tsx";
 
// This is a test component to test anything within the UI. It is not used in the functional application and can be ignored for releases.
// Author: Richard Tang

function Test() {
  const { role, email } = useAuth();

  console.log("Roles:", role);
  console.log("Email:", email);

  return (
    <div>
      <Navbar />
      <h1>Roles:</h1>
      <pre>{JSON.stringify(role, null, 2)}</pre>
      <pre>{JSON.stringify(email, null, 2)}</pre>
    </div>
  );
}

export default Test;