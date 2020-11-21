using System;
namespace Neptune
{
    public class Neptune
    {
        /// <summary>
        /// currently the tag field is only used to validate message
        /// </summary>
        public const ushort MagicTag = 13;
    }

    public enum NeptuneTranporterErrorReason
    {
        Unknown,
    }

    public enum NeptuneMessageType : ushort
    {
        None = 0,
        Normal = 1,
        Call = 2
    }
}
