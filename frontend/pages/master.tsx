
/**
 * Master Agent Page
 * Main interface for the Master Agent system
 */

import React from 'react';
import Head from 'next/head';
import { MasterDesk } from '../components/MasterDesk';

const MasterPage: React.FC = () => {
  return (
    <>
      <Head>
        <title>CPAS Master Agent - Greta</title>
        <meta name="description" content="Master Agent interface for Comprehensive Personal AI System" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <MasterDesk />
    </>
  );
};

export default MasterPage;
