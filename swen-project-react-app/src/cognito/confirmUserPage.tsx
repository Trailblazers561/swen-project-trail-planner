//https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javascriptv3/example_code/cognito-identity-provider/scenarios/cognito-developer-guide-react-example/frontend-client

import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { confirmSignUp } from "./authService";

// Currently unused page, but if SES is setup it can be used (Simple Email Service to have custom verification message)
const ConfirmUserPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [email, setEmail] = useState<string>(searchParams.get("email") ?? "");
  const [code, setCode] = useState<string>(searchParams.get("code") ?? "");

  const [confirmed, setConfirmed] = useState<boolean>(!!email && !!code);

  let attempted = false;
  useEffect(() => {
    if (confirmed && !attempted) {
      attempted = true;
      submitCode();
    }
  }, []);

  async function submitCode() {
    try {
      await confirmSignUp(email, code);
      alert("Account confirmed successfully!\nPlease close this page!");
    } catch (error) {
      setConfirmed(false);
      setSearchParams({});
      setEmail("");
      setCode("");
      alert(`Failed to confirm account: ${error}`);
    }
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!email)
      alert("Please enter a valid email");
    else if (!code)
      alert("Please enter a valid code");
    else
      await submitCode();
  };

  return (
    <div className="loginForm">
      <h2>Confirm Account</h2>
      {!confirmed && (
        <form onSubmit={handleSubmit}>
          <div>
            <input
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              required
            />
          </div>
          <div>
            <input
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Confirmation Code"
              required
            />
          </div>
          <Button type="submit" variant="primary" className="w-full">Confirm Account</Button>
        </form>
      )}
      {confirmed && (
        <h2>Account Confirmed Successfully</h2>
      )}
    </div>
  );
};

export default ConfirmUserPage;