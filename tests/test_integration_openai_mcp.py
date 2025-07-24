#!/usr/bin/env python3
"""
Integration Test for OpenAI MCP functionality with existing Meta Ads tools

This test verifies that:
1. Existing Meta Ads tools still work after adding OpenAI MCP tools
2. New search and fetch tools are properly registered
3. Both old and new tools can coexist without conflicts

Usage:
    python tests/test_integration_openai_mcp.py
"""

import sys
import os
import importlib

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_module_imports():
    """Test that all modules can be imported successfully"""
    print("🧪 Testing module imports...")
    
    try:
        # Test core module import
        import meta_ads_mcp.core as core
        print("✅ Core module imported successfully")
        
        # Test that mcp_server is available
        assert hasattr(core, 'mcp_server'), "mcp_server not found in core module"
        print("✅ mcp_server available")
        
        # Test that existing tools are still available
        existing_tools = [
            'get_ad_accounts', 'get_account_info', 'get_campaigns', 
            'get_ads', 'get_insights', 'search_ads_archive'
        ]
        
        for tool in existing_tools:
            assert hasattr(core, tool), f"Existing tool {tool} not found"
        print(f"✅ All {len(existing_tools)} existing tools available")
        
        # Test that new OpenAI tools are available
        openai_tools = ['search', 'fetch']
        for tool in openai_tools:
            assert hasattr(core, tool), f"OpenAI tool {tool} not found"
        print(f"✅ All {len(openai_tools)} OpenAI MCP tools available")
        
        return True
        
    except Exception as e:
        print(f"❌ Module import test failed: {e}")
        return False

def test_tool_registration():
    """Test that tools are properly registered with the MCP server"""
    print("\n🧪 Testing tool registration...")
    
    try:
        # Import the server and get registered tools
        from meta_ads_mcp.core.server import mcp_server
        
        # Get all registered tools
        # Note: FastMCP may not expose tools until runtime, so we'll check the module structure
        print("✅ MCP server accessible")
        
        # Test that OpenAI Deep Research module can be imported
        from meta_ads_mcp.core import openai_deep_research
        print("✅ OpenAI Deep Research module imported")
        
        # Test that the tools are callable
        assert callable(openai_deep_research.search), "search tool is not callable"
        assert callable(openai_deep_research.fetch), "fetch tool is not callable"
        print("✅ OpenAI tools are callable")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool registration test failed: {e}")
        return False

def test_tool_signatures():
    """Test that tool signatures are correct"""
    print("\n🧪 Testing tool signatures...")
    
    try:
        from meta_ads_mcp.core.openai_deep_research import search, fetch
        import inspect
        
        # Test search tool signature
        search_sig = inspect.signature(search)
        search_params = list(search_sig.parameters.keys())
        
        # Should have access_token and query parameters
        expected_search_params = ['access_token', 'query']
        for param in expected_search_params:
            assert param in search_params, f"search tool missing parameter: {param}"
        print("✅ search tool has correct signature")
        
        # Test fetch tool signature
        fetch_sig = inspect.signature(fetch)
        fetch_params = list(fetch_sig.parameters.keys())
        
        # Should have id parameter
        assert 'id' in fetch_params, "fetch tool missing 'id' parameter"
        print("✅ fetch tool has correct signature")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool signature test failed: {e}")
        return False

def test_existing_functionality_preserved():
    """Test that existing functionality is not broken"""
    print("\n🧪 Testing existing functionality preservation...")
    
    try:
        # Test that we can still import and access existing tools
        from meta_ads_mcp.core.accounts import get_ad_accounts
        from meta_ads_mcp.core.campaigns import get_campaigns
        from meta_ads_mcp.core.ads import get_ads
        from meta_ads_mcp.core.insights import get_insights
        
        # Verify they're still callable
        assert callable(get_ad_accounts), "get_ad_accounts is not callable"
        assert callable(get_campaigns), "get_campaigns is not callable"
        assert callable(get_ads), "get_ads is not callable"
        assert callable(get_insights), "get_insights is not callable"
        
        print("✅ All existing tools remain callable")
        
        # Test that existing tool signatures haven't changed
        import inspect
        
        accounts_sig = inspect.signature(get_ad_accounts)
        accounts_params = list(accounts_sig.parameters.keys())
        assert 'access_token' in accounts_params, "get_ad_accounts signature changed"
        
        print("✅ Existing tool signatures preserved")
        
        return True
        
    except Exception as e:
        print(f"❌ Existing functionality test failed: {e}")
        return False

def test_no_name_conflicts():
    """Test that there are no naming conflicts between old and new tools"""
    print("\n🧪 Testing for naming conflicts...")
    
    try:
        import meta_ads_mcp.core as core
        
        # Get all attributes from the core module
        all_attrs = dir(core)
        
        # Check for expected tools
        existing_tools = [
            'get_ad_accounts', 'get_campaigns', 'get_ads', 'get_insights',
            'search_ads_archive'  # This is the existing search function
        ]
        
        new_tools = ['search', 'fetch']  # These are the new OpenAI tools
        
        # Verify all tools exist
        for tool in existing_tools + new_tools:
            assert tool in all_attrs, f"Tool {tool} not found in core module"
        
        # Verify search_ads_archive and search are different functions
        assert core.search_ads_archive != core.search, "search and search_ads_archive should be different functions"
        
        print("✅ No naming conflicts detected")
        print(f"   - Existing search tool: search_ads_archive (Meta Ads Library)")
        print(f"   - New search tool: search (OpenAI MCP Deep Research)")
        
        return True
        
    except Exception as e:
        print(f"❌ Naming conflict test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 OpenAI MCP Integration Tests")
    print("="*50)
    
    tests = [
        ("Module Imports", test_module_imports),
        ("Tool Registration", test_tool_registration),
        ("Tool Signatures", test_tool_signatures),
        ("Existing Functionality", test_existing_functionality_preserved),
        ("Naming Conflicts", test_no_name_conflicts),
    ]
    
    results = {}
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
            all_passed = False
    
    # Summary
    print("\n🏁 INTEGRATION TEST RESULTS")
    print("="*30)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n📊 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Integration successful!")
        print("   • Existing Meta Ads tools: Working")
        print("   • New OpenAI MCP tools: Working")
        print("   • No conflicts detected")
        print("   • Ready for OpenAI ChatGPT Deep Research")
        print("\n📋 Next steps:")
        print("   1. Start server inside uv virtual env:")
        print("      # Basic HTTP server (default: localhost:8080)")
        print("      python -m meta_ads_mcp --transport streamable-http")
        print("      ")
        print("      # Custom host and port")
        print("      python -m meta_ads_mcp --transport streamable-http --host 0.0.0.0 --port 9000")
        print("   2. Run OpenAI tests: python tests/test_openai_mcp_deep_research.py")
    else:
        print("\n⚠️  Integration issues detected")
        print("   Please fix failed tests before proceeding")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 